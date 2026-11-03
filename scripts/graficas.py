"""Gráficos reproducibles de evaluación (métricas calculadas sobre datos sintéticos)."""
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figuras';FIG.mkdir(exist_ok=True)
m=json.loads((ROOT/'model/metricas_evaluacion.json').read_text(encoding='utf-8'))

matrix=np.array(m['matriz_confusion'])
fig, ax=plt.subplots(figsize=(9,7.4))
im=ax.imshow(matrix,cmap='Blues')
ax.figure.colorbar(im,ax=ax,fraction=.046,pad=.04)
labels=[s.replace('consulta_clinica','consulta clínica') for s in m['etiquetas']]
ax.set(xticks=np.arange(len(labels)),yticks=np.arange(len(labels)),xticklabels=labels,yticklabels=labels,
       xlabel='Predicción',ylabel='Categoría real',title='Matriz de confusión | Evaluación sintética (n=39)')
plt.setp(ax.get_xticklabels(),rotation=35,ha='right',rotation_mode='anchor')
for i in range(len(labels)):
 for j in range(len(labels)):
  ax.text(j,i,str(matrix[i,j]),ha='center',va='center',color='white' if matrix[i,j]>matrix.max()/2 else 'black',fontsize=11)
fig.tight_layout();fig.savefig(FIG/'matriz_confusion.png',dpi=185,bbox_inches='tight');plt.close(fig)

x=np.arange(2)
width=.36
fig,ax=plt.subplots(figsize=(9,5.5))
ax.bar(x-width/2,[m['baseline_mayoria_accuracy']*100,m['baseline_mayoria_f1_macro']*100],width,label='Baseline: clase mayoritaria')
ax.bar(x+width/2,[m['accuracy']*100,m['f1_macro']*100],width,label='TF-IDF + Regresión logística')
ax.set_ylim(0,100);ax.set_ylabel('Porcentaje (%)')
ax.set_xticks(x,['Exactitud','F1 macro']);ax.set_title('Comparación de modelos | Evaluación sintética')
ax.legend(loc='upper left')
ax.grid(axis='y',alpha=.15)
for bars in ax.containers:
 ax.bar_label(bars,fmt='%.1f%%',padding=3)
fig.tight_layout();fig.savefig(FIG/'comparacion_metricas.png',dpi=185,bbox_inches='tight');plt.close(fig)
print('Figuras guardadas en',FIG)
