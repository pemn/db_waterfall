#!python
# create a standard waterfall chart between two datasets
# groups_a, groups_b: the classification variable(s) to observe changes (ex.: lito)
# value_a, value_b: (optional) a numeric variable with the quantity of change (ex.: volume)
# more details on manual
# v1.0 2023/11 paulo.ernesto
'''
usage: $0 input_a*csv,xlsx groups_a#group_a:input_a value_a:input_a input_b*csv,xlsx groups_b#group_b:input_b value_b:input_b condition output*png display@
'''
import sys, os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, commalist, pd_load_dataframe, pd_save_dataframe, log

def pd_waterfall(ax, v_0, v_1, name_a, name_b):
  cmap = plt.get_cmap()

  ci = v_0.index.union(v_1.index)
  v_0 = v_0.reindex(ci, fill_value=0)
  v_1 = v_1.reindex(ci, fill_value=0)
  s_1_0 = v_1.subtract(v_0)
  b_x = np.concatenate((np.full(v_0.size, 0, np.int_), np.arange(1, s_1_0.size + 1), np.full(v_1.size, s_1_0.size + 1, np.int_)))

  b_h = np.concatenate((v_0, np.fabs(s_1_0), v_1))
  c_0 = np.cumsum(v_0)
  c_1 = np.cumsum(v_1)

  c_b = np.add(np.cumsum(s_1_0), np.max(c_0))
  b_b = np.concatenate((np.subtract(c_0, v_0), np.subtract(c_b, np.fabs(s_1_0)), np.subtract(c_1, v_1)))
  
  s_c = np.linspace(0, 1, s_1_0.size)
  b_c = np.concatenate((s_c.take(np.arange(v_0.size)), s_c, s_c.take(np.arange(v_1.size))))

  b_p = ax.bar(b_x, b_h, 0.5, bottom=b_b, color=cmap(b_c), edgecolor='w')
  if sys.hexversion < 0x3080000:
    # polyfill for lack of bar_label
    for i in range(b_h.size):
      ax.annotate(int(b_h[i] + 0.5), [b_x[i] + 0.1, b_b[i] + b_h[i] * 0.5])
  else:
    ax.bar_label(b_p, label_type='center')

  l_x = np.reshape(np.stack((np.arange(0.5,s_1_0.size), np.arange(1.5,s_1_0.size+1))), (-1,), order='F')
  ax.plot(l_x, np.repeat(c_b, 2), color='k', ls='-.')
  ax.set_yticks(np.cumsum(v_0), minor=False)
  ax.grid(True, 'major', 'y', linestyle='solid')
  # for combatibility with python 3.5 we call set_xtickslabels separately
  ax.set_xticks(np.arange(s_1_0.size + 2))
  ax.set_xticklabels([name_a] + [' '.join(map(str,_)) if isinstance(_,tuple) else _ for _ in s_1_0.index] + [name_b])



def db_waterfall(input_a, groups_a, value_a, input_b, groups_b, value_b, condition, output, display):
  g_a = commalist(groups_a).split()
  g_b = commalist(groups_b).split()

  df_a = pd_load_dataframe(input_a, condition, None, g_a + [value_a])
  df_b = pd_load_dataframe(input_b, condition, None, g_b + [value_b])
  name_a = os.path.splitext(os.path.basename(input_a))[0]
  name_b = os.path.splitext(os.path.basename(input_b))[0]

  if not value_a:
    value_a = 'n'
    df_a[value_a] = np.ones(df_a.shape[0])
  if not value_b:
    value_b = 'n'
    df_b[value_b] = np.ones(df_b.shape[0])
  plt.set_cmap('Spectral')

  pt_a = df_a.pivot_table(value_a, g_a, None, 'sum')
  pt_b = df_b.pivot_table(value_b, g_b, None, 'sum')

  pd_waterfall(plt.gca(), pt_a.squeeze(), pt_b.squeeze(), name_a, name_b)


  if int(display):
    plt.show()

  log("finished")

main = db_waterfall

if __name__=="__main__":
  usage_gui(__doc__)
