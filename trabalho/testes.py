import subprocess
import statistics
import argparse
import csv
import os
import time
from datetime import datetime

TARGETS = [
    {'name': 'Nginx', 'host': '60.45.0.10', 'port': 80},
    {'name': 'Apache', 'host': '60.45.0.20', 'port': 80}
]

def run_client(host, port, path, requests, matricula, nome, outfile):
    cmd = [
        "python3", "cliente.py",
        "--host", host,
        "--port", str(port),
        "--path", path,
        "--requests", str(requests),
        "--matricula", matricula,
        "--nome", nome,
        "--out", outfile
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res

def parse_csv(file):
    lat = []
    try:
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['latency'] and row['latency'].strip():
                    lat.append(float(row['latency']))
    except Exception:
        return []
    return lat

def summary(latencies):
    if not latencies:
        return {'n': 0, 'mean': 0, 'stdev': 0, 'min': 0, 'max': 0}
    return {
        'n': len(latencies),
        'mean': statistics.mean(latencies),
        'stdev': statistics.pstdev(latencies) if len(latencies) > 1 else 0,
        'min': min(latencies),
        'max': max(latencies)
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--requests', type=int, default=500, help='Requisições por rodada')
    parser.add_argument('--runs', type=int, default=10, help='Número de rodadas (Min 10 pelo PDF)')
    parser.add_argument('--outdir', default='results')
    args = parser.parse_args()

    matricula = '20229036045'
    nome = 'Walison'

    os.makedirs(args.outdir, exist_ok=True)
    summary_file = os.path.join(args.outdir, 'relatorio_final.csv')
    
    print(f"--- INICIANDO BATERIA DE TESTES ---")
    print(f"Aluno: {nome} | Matrícula: {matricula}")
    print(f"Configuração: {args.runs} rodadas de {args.requests} requisições cada.\n")

    with open(summary_file, 'w', newline='') as sf:
        writer = csv.writer(sf)
        writer.writerow(['timestamp','server','ip','run','mean_latency','stdev','min','max'])
        
        for server in TARGETS:
            print(f"Testando Servidor: {server['name']} ({server['host']})")
            time.sleep(2)
            
            for r in range(args.runs):
                out_csv = os.path.join(args.outdir, f"{server['name']}_run_{r+1}.csv")
                
                res = run_client(server['host'], server['port'], '/', args.requests, matricula, nome, out_csv)
                
                if res.returncode != 0:
                    print(f"   [ERRO] Falha na execução {r+1}")
                    continue
                
                lat = parse_csv(out_csv)
                s = summary(lat)
                
                writer.writerow([datetime.now().isoformat(), server['name'], server['host'], r+1, s['mean'], s['stdev'], s['min'], s['max']])
                print(f"   -> Rodada {r+1}/{args.runs}: Média {s['mean']:.4f}s | Max {s['max']:.4f}s")

if __name__ == '__main__':
    main()