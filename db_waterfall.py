#!python
# create a standard waterfall chart between two datasets
# groups_a, groups_b: the classification variable(s) to observe changes (ex.: lito)
# value_a, value_b: (optional) a numeric variable with the quantity of change (ex.: volume)
# more details on manual
# v1.0 2023/11 paulo.ernesto
'''
usage: $0 input_a*csv,xlsx groups_a#group_a:input_a value_a:input_a input_b*csv,xlsx groups_b#group_b:input_b value_b:input_b condition output*png,xlsx display@
'''
import sys, os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.chart import Reference, Series, BarChart, StockChart, ScatterChart
from openpyxl.chart.label import DataLabelList
from collections import OrderedDict
from openpyxl.drawing.image import Image as XLImage
from PIL import Image
from binascii import a2b_hex
from io import BytesIO

# Reference(worksheet=None, min_col=None, min_row=None, max_col=None, max_row=None, range_string=None)
# BarChart(gapWidth=150, overlap=None, serLines=None, extLst=None, **kw)
# add_data(self, data, from_rows=False, titles_from_data=False)
# SeriesFactory(values, xvalues=None, zvalues=None, title=None, title_from_data=False)
# Series(idx=0, order=0, tx=None, spPr=None, pictureOptions=None, dPt=(), dLbls=None, trendline=None, errBars=None, cat=None, val=None, invertIfNegative=None, shape=None, xVal=None, yVal=None, bubbleSize=None, bubble3D=None, marker=None, smooth=None, explosion=None, extLst=None)

# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, commalist, pd_load_dataframe, pd_save_dataframe, log


def pd_waterfall(vs, names, output, display):
  plt.set_cmap('Spectral')
  ax = plt.gca()
  cmap = plt.get_cmap()

  ci = vs[0].index.union(vs[1].index)
  vs[0] = vs[0].reindex(ci, fill_value=0)
  vs[1] = vs[1].reindex(ci, fill_value=0)
  s_1_0 = vs[1].subtract(vs[0])
  b_x = np.concatenate((np.full(vs[0].size, 0, np.int_), np.arange(1, s_1_0.size + 1), np.full(vs[1].size, s_1_0.size + 1, np.int_)))

  b_h = np.concatenate((vs[0], np.fabs(s_1_0), vs[1]))
  c_0 = np.cumsum(vs[0])
  c_1 = np.cumsum(vs[1])

  c_b = np.add(np.cumsum(s_1_0), np.max(c_0))
  b_b = np.concatenate((np.subtract(c_0, vs[0]), np.subtract(c_b, np.fabs(s_1_0)), np.subtract(c_1, vs[1])))
  
  s_c = np.linspace(0, 1, s_1_0.size)
  b_c = np.concatenate((s_c.take(np.arange(vs[0].size)), s_c, s_c.take(np.arange(vs[1].size))))

  b_p = ax.bar(b_x, b_h, 0.5, bottom=b_b, color=cmap(b_c), edgecolor='w')
  if sys.hexversion < 0x3080000:
    # polyfill for lack of bar_label
    for i in range(b_h.size):
      ax.annotate(int(b_h[i] + 0.5), [b_x[i] + 0.1, b_b[i] + b_h[i] * 0.5])
  else:
    ax.bar_label(b_p, label_type='center')

  l_x = np.reshape(np.stack((np.arange(0.5,s_1_0.size), np.arange(1.5,s_1_0.size+1))), (-1,), order='F')
  ax.plot(l_x, np.repeat(c_b, 2), color='k', ls='-.')
  ax.set_yticks(np.cumsum(vs[0]), minor=False)
  ax.grid(True, 'major', 'y', linestyle='solid')
  # for combatibility with python 3.5 we call set_xtickslabels separately
  ax.set_xticks(np.arange(s_1_0.size + 2))
  ax.set_xticklabels(names[:1] + [' '.join(map(str,_)) if isinstance(_,tuple) else _ for _ in s_1_0.index] + names[1:])

  if output:
    plt.savefig(output)

  if int(display):
    plt.show()

def k2j_append(ws, vs, ks):
  cs = sum([vs[0].get(_,0) for _ in ks])
  for i in range(2,len(ks)):
    row = [None] * len(ks)
    d = None
    for j in range(2,len(ks)):
      if i == j:
        d = vs[1].get(ks[j],0) - vs[0].get(ks[j],0)
        cs += d
        row[j] = abs(d)

    row[0] = ks[i]
    row[1] = cs - abs(d)

    ws.append(row)


def xl_waterfall(vs, names, output, display, group = 'waterfall'):
  wb = openpyxl.Workbook()
  ws = wb.active

  k2j = OrderedDict()
  k2j[None] = 0
  k2j[group] = 1
  for i in range(len(vs)):
    for k,v in vs[i].items():
      if isinstance(k, tuple):
        k = str.join('_',map(str,k))
      if k not in k2j:
        k2j[k] = len(k2j)
  
  ks = list(k2j.keys())
  ws.append(ks)
  for i in range(len(vs)):
    row = [None] * len(k2j)
    row[0] = names[i]
    for k,v in vs[i].items():
      if isinstance(k, tuple):
        k = str.join('_', map(str,k))
      row[k2j[k]] = v

    if i == 1:
      k2j_append(ws, vs, ks)
    ws.append(row)

  c0 = BarChart()

  c0.grouping = "stacked"
  c0.overlap = 100

  for i in range(1,len(k2j)):
    val = Reference(ws, i+1, 1, i+1, len(vs)+len(ks))
    c0.series.append(Series(val, title_from_data=True))
  
  # first series in just a helper to make the waterfall bars "float"
  c0.dLbls = DataLabelList()
  c0.dLbls.showVal = True
  c0.ser[0].graphicalProperties.noFill = True
  c0.ser[0].dLbls = DataLabelList()

  c0.set_categories(Reference(ws, 1, 2, 1, len(vs)+len(ks)))

  ws.add_chart(c0)

  if output:
    wb.save(output)
    if int(display):
      os.startfile(output)

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

  pt_a = df_a.pivot_table(value_a, g_a, None, 'sum')
  pt_b = df_b.pivot_table(value_b, g_b, None, 'sum')

  if output.lower().endswith('png'):
    pd_waterfall([pt_a.squeeze(), pt_b.squeeze()], [name_a, name_b], output, display)
  if output.lower().endswith('xlsx'):
    xl_waterfall([pt_a.squeeze(), pt_b.squeeze()], [name_a, name_b], output, display, str.join('_',g_a))

  log("finished")

main = db_waterfall

if __name__=="__main__":
  usage_gui(__doc__)
