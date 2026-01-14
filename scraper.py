import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# URLs de TODAS las categorías normativas
URLS = {
    'circulares': 'https://www.supereduc.cl/categoria-normativa/circulares/',
    'oficios': 'https://www.supereduc.cl/categoria-normativa/oficios/',
    'dictamenes': 'https://www.supereduc.cl/categoria-normativa/dictamenes/',
    'jurisprudencia': 'https://www.supereduc.cl/categoria-normativa/jurisprudencia/',
    'resoluciones': 'https://www.supereduc.cl/categoria-normativa/resoluciones/',
}

def explore_page_structure(url, category_name):
    """Explora la estructura de la página para entender cómo extraer datos"""
    print(f"\n{'='*70}")
    print(f"Explorando: {category_name.upper()}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        # Verificar si la página cargó correctamente
        if response.status_code != 200:
            print(f"⚠️  Error HTTP {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Estrategia 1: Buscar artículos (común en WordPress)
        articles = soup.find_all('article')
        if articles and len(articles) > 0:
            print(f"✓ Encontré {len(articles)} elementos <article>")
            print(f"\nEstructura del primer elemento:")
            print("-" * 70)
            print(articles[0].prettify()[:800])
            print("\n... (truncado)")
            print("-" * 70)
            
            # Intentar extraer información básica
            first = articles[0]
            title = first.find(['h1', 'h2', 'h3', 'h4'])
            link = first.find('a', href=True)
            print(f"\nExtracción de prueba:")
            print(f"  Título: {title.get_text(strip=True) if title else 'No encontrado'}")
            print(f"  Enlace: {link['href'] if link else 'No encontrado'}")
        
        # Estrategia 2: Buscar divs con clases típicas
        else:
            possible_containers = soup.find_all('div', class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['post', 'item', 'entry', 'content', 'documento']
            ))
            if possible_containers:
                print(f"✓ Encontré {len(possible_containers)} contenedores tipo post/item")
                print(f"\nMuestra del primero:")
                print("-" * 70)
                print(possible_containers[0].prettify()[:800])
                print("\n... (truncado)")
                print("-" * 70)
        
        # Estrategia 3: Buscar todos los enlaces (fallback)
        all_links = soup.find_all('a', href=True)
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"  Total de enlaces: {len(all_links)}")
        
        # Filtrar enlaces relevantes
        pdf_links = [a for a in all_links if '.pdf' in a.get('href', '').lower()]
        internal_links = [a for a in all_links if 'supereduc.cl' in a.get('href', '') 
                         and not any(skip in a.get('href', '') for skip in ['wp-content', 'wp-admin', 'categoria-normativa'])]
        
        print(f"  Enlaces a PDFs: {len(pdf_links)}")
        print(f"  Enlaces internos relevantes: {len(internal_links)}")
        
        if pdf_links:
            print(f"\n📄 Ejemplos de PDFs encontrados:")
            for i, link in enumerate(pdf_links[:5], 1):
                text = link.get_text(strip=True)[:80]
                href = link['href']
                print(f"  {i}. {text}")
                print(f"     → {href}")
        
        if internal_links:
            print(f"\n🔗 Ejemplos de enlaces internos:")
            for i, link in enumerate(internal_links[:3], 1):
                text = link.get_text(strip=True)[:80]
                href = link['href']
                print(f"  {i}. {text}")
                print(f"     → {href}")
        
        # Buscar estructuras de paginación
        pagination = soup.find_all(['nav', 'div'], class_=lambda x: x and 'pag' in str(x).lower())
        if pagination:
            print(f"\n📖 Sistema de paginación detectado ({len(pagination)} elementos)")
        
        return soup
        
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout al intentar conectar (>15 segundos)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def main():
    """Función principal que ejecuta la exploración"""
    print("\n" + "="*70)
    print("EXPLORADOR DE ESTRUCTURA - SUPEREDUC NORMATIVA")
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    
    for category, url in URLS.items():
        soup = explore_page_structure(url, category)
        results[category] = {
            'success': soup is not None,
            'timestamp': datetime.now().isoformat()
        }
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE EXPLORACIÓN")
    print("="*70)
    successful = sum(1 for r in results.values() if r['success'])
    print(f"✓ Categorías exploradas exitosamente: {successful}/{len(URLS)}")
    print(f"✗ Categorías con error: {len(URLS) - successful}")
    
    for cat, result in results.items():
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {cat}")
    
    print("\n" + "="*70)
    print("Próximo paso: Analizar los logs para crear los selectores CSS correctos")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
