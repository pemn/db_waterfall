#!python
# create a waterfall chart between reserves
# groups, groups_b: the classification variable(s) to observe changes (ex.: lito)
# value_a, value_b: (optional) a numeric variable with the quantity of change (ex.: volume)
# more details on manual
# v1.0 2023/11 paulo.ernesto
'''
usage: $0 input_files#reserve*csv,xlsx condition groups#group:input_files value:input_files value_divide=1,1000,1000000 output*png,xlsx display@
'''
import sys, os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.chart import Reference, Series, BarChart, StockChart, ScatterChart
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.trendline import Trendline
from collections import OrderedDict

# Reference(worksheet=None, min_col=None, min_row=None, max_col=None, max_row=None, range_string=None)
# BarChart(gapWidth=150, overlap=None, serLines=None, extLst=None, **kw)
# add_data(self, data, from_rows=False, titles_from_data=False)
# SeriesFactory(values, xvalues=None, zvalues=None, title=None, title_from_data=False)
# Series(idx=0, order=0, tx=None, spPr=None, pictureOptions=None, dPt=(), dLbls=None, trendline=None, errBars=None, cat=None, val=None, invertIfNegative=None, shape=None, xVal=None, yVal=None, bubbleSize=None, bubble3D=None, marker=None, smooth=None, explosion=None, extLst=None)

# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, commalist, pd_load_dataframe, pd_save_dataframe, log


def pd_waterfall_reserves(pt, output, display):
  plt.set_cmap('Spectral')
  ax = plt.gca()
  cmap = plt.get_cmap()

  pts = pt.squeeze()

  d_0 = np.diff(pts)
  b_x = np.arange(pt.shape[0] + 1)
  b_h = np.concatenate([pts[:1], d_0, pts[-1:]])
  b_b = np.concatenate([np.zeros(1), pts[:-1], np.zeros(1)])
  b_c = np.linspace(0, 1, pt.shape[0] + 1)
  b_p = ax.bar(b_x, b_h, 0.5, bottom=b_b, color=cmap(b_c), edgecolor='w')
  ax.bar_label(b_p, label_type='center')

  l_x = np.reshape(np.stack((np.arange(0.5,b_x.size-2), np.arange(1.5,b_x.size-1))), (-1,), order='F')
  #print(l_x)
  ax.plot(l_x, np.repeat(b_b[1:-1], 2), color='k', ls='-.')
  ax.set_xticks(b_x)
  ax.set_xticklabels(np.concatenate([pt.index, [pt.index.name]]))

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
    row[1] = cs - max(0, d)

    ws.append(row)


def xl_waterfall_reserves(pt, output, display):
  wb = openpyxl.Workbook()
  ws = wb.active
  pts = pt.squeeze()

  ws.append([None, None, pts.name])
  diff0 = None
  for ri, rd in pts.items():
    if diff0 is None:
      ws.append([ri,None,rd])
    else:
      d = rd - diff0
      ws.append([ri,rd - max(0, d),abs(d)])
    diff0 = rd
  else:
    ws.append([pt.index.name,None,rd])
    
  c0 = BarChart(overlap=100, grouping = "stacked", dLbls = DataLabelList(showVal = True))
  val = Reference(ws, 2, 1, 2, pts.size+2)
  c0.series.append(Series(val, title_from_data=True))
  val = Reference(ws, 3, 1, 3, pts.size+2)
  c0.series.append(Series(val, title_from_data=True))
  c0.set_categories(Reference(ws, 1, 2, 1, pts.size+2))

  c0.ser[0].graphicalProperties.noFill = True
  c0.ser[0].dLbls = DataLabelList()
  c0.ser[0].trendline = Trendline(trendlineType='movingAvg', period=2)
  c0.ser[0].trendline.showVal = False
  c0.legend = None

  ws.add_chart(c0)

  if output:
    wb.save(output)
    if int(display):
      os.startfile(output)

def db_waterfall_reserves(input_files, condition, groups, value, value_divide, output, display):
  fl = commalist(input_files).split()
  gl = commalist(groups).split()
  if not value_divide:
    value_divide = 1
  else:
    value_divide = float(value_divide)
  
  dfa = None
  for f in fl:
    print(f)
    df = pd_load_dataframe(f, condition, None, gl + [value])
    if dfa is None:
      dfa = df
    else:
      dfa = pd.concat([dfa, df])

  if not value:
    value = 'count'
    dfa[value] = 1

  pt = dfa.pivot_table(value, gl, None, 'sum', sort=False)
  pt /= value_divide
  pt = pt.round(0)

  if output.lower().endswith('xlsx'):
    xl_waterfall_reserves(pt, output, display)
  else:
    pd_waterfall_reserves(pt, output, display)

  log("finished")

main = db_waterfall_reserves

if __name__=="__main__":
  usage_gui(__doc__)
