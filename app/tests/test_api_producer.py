#!/usr/bin/env python
"""
Script de teste para API REST do Producer Service
"""
import requests
import time
import sys

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Testa endpoint de health check"""
    print("\n🔍 Testando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✅ Health check OK!")
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def test_trigger_simple():
    """Testa trigger simples via URL"""
    print("\n🔍 Testando Trigger Simples (POST /trigger/1)...")
    try:
        response = requests.post(f"{BASE_URL}/trigger/1")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert 'job_id' in data
        
        print(f"   ✅ Evento enfileirado! Job ID: {data['job_id']}")
        return data['job_id']
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None


def test_trigger_with_timestamp():
    """Testa trigger com timestamp específico"""
    print("\n🔍 Testando Trigger com Timestamp...")
    try:
        payload = {
            "channel": 2,
            "timestamp": "2026-02-18 16:00:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/trigger",
            json=payload
        )
        
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        assert response.status_code == 200
        assert data['channel'] == 2
        assert data['timestamp'] == "2026-02-18 16:00:00"
        
        print(f"   ✅ Evento com timestamp enfileirado! Job ID: {data['job_id']}")
        return data['job_id']
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None


def test_trigger_with_query_string():
    """Testa trigger com timestamp via query string"""
    print("\n🔍 Testando Trigger com Query String...")
    try:
        timestamp = "2026-02-18 17:30:00"
        response = requests.post(
            f"{BASE_URL}/trigger/3",
            params={"timestamp": timestamp}
        )
        
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        assert response.status_code == 200
        assert data['channel'] == 3
        assert data['timestamp'] == timestamp
        
        print(f"   ✅ Evento via query string enfileirado! Job ID: {data['job_id']}")
        return data['job_id']
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None


def test_job_status(job_id):
    """Testa consulta de status do job"""
    if not job_id:
        print("\n⚠️  Pulando teste de status (sem job_id)")
        return False
    
    print(f"\n🔍 Testando Status do Job ({job_id})...")
    try:
        response = requests.get(f"{BASE_URL}/status/{job_id}")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        assert response.status_code == 200
        assert data['job_id'] == job_id
        
        print(f"   ✅ Status: {data['status']}")
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def test_validation_errors():
    """Testa validações de erro"""
    print("\n🔍 Testando Validações de Erro...")
    
    # Teste 1: Canal fora do range
    print("   • Testando canal inválido (99)...")
    response = requests.post(f"{BASE_URL}/trigger", json={"channel": 99})
    assert response.status_code == 400
    print("     ✅ Validação OK (canal inválido rejeitado)")
    
    # Teste 2: Sem JSON
    print("   • Testando sem JSON...")
    response = requests.post(f"{BASE_URL}/trigger")
    assert response.status_code == 400
    print("     ✅ Validação OK (JSON obrigatório)")
    
    # Teste 3: Sem campo channel
    print("   • Testando sem campo 'channel'...")
    response = requests.post(f"{BASE_URL}/trigger", json={"timestamp": "2026-02-18 16:00:00"})
    assert response.status_code == 400
    print("     ✅ Validação OK (campo 'channel' obrigatório)")
    
    print("   ✅ Todas as validações passaram!")
    return True


def main():
    """Executa todos os testes"""
    print("="*70)
    print("🧪 TESTE DA API REST - PRODUCER SERVICE")
    print("="*70)
    print(f"\nBase URL: {BASE_URL}")
    print("Certifique-se de que o producer_service está rodando!")
    print("\nIniciando testes em 2 segundos...")
    time.sleep(2)
    
    results = []
    
    # Teste 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Teste 2: Trigger Simples
    job_id = test_trigger_simple()
    results.append(("Trigger Simples", job_id is not None))
    
    # Teste 3: Trigger com Timestamp
    job_id2 = test_trigger_with_timestamp()
    results.append(("Trigger com Timestamp", job_id2 is not None))
    
    # Teste 4: Trigger com Query String
    job_id3 = test_trigger_with_query_string()
    results.append(("Trigger Query String", job_id3 is not None))
    
    # Teste 5: Status do Job
    results.append(("Status do Job", test_job_status(job_id)))
    
    # Teste 6: Validações de Erro
    results.append(("Validações", test_validation_errors()))
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n  Total: {passed}/{len(results)} testes passaram")
    print("="*70 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
