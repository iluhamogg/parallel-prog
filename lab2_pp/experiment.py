import argparse, csv, os, platform, re, subprocess, sys, statistics
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--exe',default='matrix.exe' if os.name=='nt' else './matrix')
p.add_argument('--sizes',nargs='+',type=int,default=[200,400,800,1200,1600,2000])
p.add_argument('--threads',nargs='+',type=int,default=[1,2,4,8,16])
p.add_argument('--environment',default=platform.platform())
p.add_argument('--repeats',type=int,default=3)
a=p.parse_args()
if a.repeats < 1: p.error('Positive repeat count required')
if 1 not in a.threads or min(a.sizes+a.threads)<1: p.error('Positive values and one thread required')
Path('results').mkdir(exist_ok=True)
rows=[]
for n in a.sizes:
    subprocess.run([sys.executable,'generate.py',str(n)],check=True)
    for t in sorted(set(a.threads)):
        samples=[]
        for repeat in range(a.repeats):
            r=subprocess.run([a.exe,'A.txt','B.txt','result.txt',str(t)],capture_output=True,text=True,check=True)
            samples.append(float(re.search(r'time_sec=([0-9.]+)',r.stdout)[1]))
            subprocess.run([sys.executable,'check.py'],check=True,env={**os.environ,'OPENBLAS_NUM_THREADS':'1'})
        sec=statistics.median(samples)
        if t==1: base=sec
        rows.append(dict(N=n,threads=t,time_sec=sec,speedup=base/sec,efficiency=100*base/sec/t,verified='PASS',samples_sec=';'.join(map(str,samples))))
        print(n,t,sec,flush=True)
        with open('results/windows_results.csv','w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
for field,label in [('time_sec','Time (s)'),('speedup','Speedup'),('efficiency','Efficiency (%)')]:
    plt.figure(figsize=(8,5))
    for t in sorted(set(a.threads)):
        g=[r for r in rows if r['threads']==t]; plt.plot([r['N'] for r in g],[r[field] for r in g],marker='o',label=f'{t} threads')
    plt.xlabel('Matrix size N'); plt.ylabel(label); plt.legend(); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig(f'results/windows_{field}.png',dpi=150); plt.close()
block=f'\nСреда: {a.environment}. Повторений: {a.repeats}. В таблице приведена медиана времени.\n\n| N | Потоки | Время, с | Ускорение | Эффективность, % | Проверка |\n|---:|---:|---:|---:|---:|:---:|\n'
for r in rows: block+=f"| {r['N']} | {r['threads']} | {r['time_sec']:.6f} | {r['speedup']:.3f} | {r['efficiency']:.2f} | PASS |\n"
for field in ['time_sec','speedup','efficiency']: block+=f'\n![{field}](results/windows_{field}.png)\n'
block+='\n## Выводы\n\n'
for n in a.sizes:
    best=min((r for r in rows if r['N']==n),key=lambda r:r['time_sec']); block+=f"- N={n}: минимальное время {best['time_sec']:.6f} с при {best['threads']} потоках, ускорение {best['speedup']:.2f}.\n"
block+='\nВсе результаты проверены NumPy. Ускорение ограничено ресурсами процессора, памятью и накладными расходами OpenMP. Отдельные замеры сохранены в CSV.\n'
f=Path('README.md'); s=f.read_text(encoding='utf-8'); f.write_text(s.split('<!-- WINDOWS START -->')[0]+'<!-- WINDOWS START -->\n'+block+'<!-- WINDOWS END -->\n',encoding='utf-8')
