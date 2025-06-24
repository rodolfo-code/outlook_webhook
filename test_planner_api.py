#!/usr/bin/env python3
"""
Script de teste para a API de Grupos do Planner
"""

import asyncio
import httpx
import json
import traceback
import time

async def test_planner_api():
    """
    Testa a API de grupos do planner
    """
    
    # URL base da API (ajuste conforme necessário)
    base_url = "http://localhost:3000"
    
    test_email = "AlexW@w7drx.onmicrosoft.com"
    
    # Primeiro, vamos verificar se a aplicação está rodando
    print("🔍 Verificando se a aplicação está rodando...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Teste básico primeiro
            print(f"Testando endpoint básico: {base_url}/webhook")
            basic_response = await client.get(f"{base_url}/webhook")
            print(f"✅ Aplicação está respondendo! Status: {basic_response.status_code}")
            
            print(f"\n🚀 Testando busca de grupos para: {test_email}")
            print("-" * 50)
            
            # Faz a requisição para a API com timeout mais longo
            response = await client.get(
                f"{base_url}/api/planner",
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Sucesso! Grupos encontrados:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Mostra estatísticas
                groups = data.get("groups", [])
                print(f"\n📊 Estatísticas:")
                print(f"   - Total de grupos: {len(groups)}")
                
                # Conta tipos de grupos
                group_types = {}
                for group in groups:
                    types = group.get("group_types", [])
                    for group_type in types:
                        group_types[group_type] = group_types.get(group_type, 0) + 1
                
                if group_types:
                    print(f"   - Tipos de grupos:")
                    for group_type, count in group_types.items():
                        print(f"     * {group_type}: {count}")
                
            elif response.status_code == 403:
                print("❌ Erro de permissão (403)")
                print("O aplicativo não tem permissões suficientes no Azure AD.")
                print("\n🔧 Para resolver:")
                print("1. Acesse o Azure Portal (portal.azure.com)")
                print("2. Vá para Azure Active Directory > Registros de aplicativo")
                print("3. Encontre seu aplicativo e clique em 'Permissões de API'")
                print("4. Adicione as permissões: User.Read.All, Group.Read.All, GroupMember.Read.All, Directory.Read.All")
                print("5. Clique em 'Conceder consentimento de administrador'")
                print("6. Aguarde alguns minutos e teste novamente")
                print(f"\nDetalhes do erro: {response.text}")
                
            elif response.status_code == 404:
                print("❌ Usuário não encontrado (404)")
                print("Verifique se o email está correto e se o usuário existe no tenant")
                print(f"Email testado: {test_email}")
                
            elif response.status_code == 500:
                print("❌ Erro interno do servidor (500)")
                print("Verifique os logs da aplicação para mais detalhes")
                print(f"Resposta: {response.text}")
                
            else:
                print(f"❌ Erro inesperado: {response.status_code}")
                print(f"Resposta: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Erro de conexão")
            print("Verifique se a aplicação está rodando em http://localhost:3000")
            print("Para iniciar a aplicação, execute: python app/main.py")
            
        except httpx.TimeoutException:
            print("❌ Timeout na requisição (30 segundos)")
            print("A aplicação pode estar sobrecarregada ou não está respondendo")
            print("Tente reiniciar a aplicação: python app/main.py")
            
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
            print("Detalhes do erro:")
            print(traceback.format_exc())

def main():
    """
    Função principal
    """
    print("🚀 Testando API de Grupos do Planner")
    print("=" * 50)
    
    # Executa o teste
    asyncio.run(test_planner_api())
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    main() 