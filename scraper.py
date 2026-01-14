import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import random

# URLs de TODAS las categorías normativas
URLS = {
    'circulares': 'https://www.supereduc.cl/categoria-normativa/circulares/',
    'oficios': 'https://www.supereduc.cl/categoria-normativa/oficios/',
    'dictamenes': 'https://www.supereduc.cl/categoria-normativa/dictamenes/',
    'jurisprudencia': 'https://www.supereduc.cl/categoria-normativa/jurisprudencia/',
    'resoluciones': 'https://www.supereduc.cl/categoria-normativa/resoluciones/',
}

def get_headers():
    """Headers más realistas para parecer un navegador normal"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }

def explore_page_structure(url, category_name):
    """Explora la estructura de la página con técnicas anti-bloqueo"""
    print(f"\n{'='*70}")
    print(f"Explorando: {category_name.upper()}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    # Espera aleatoria para parecer más humano
    wait_time = random.uniform(2, 5)
    print(f"⏳ Esperando {wait_time:.1f}s antes de conectar...")
    time.sleep(wait_time)
    
    session = requests.Session()
    
    try:
        # Primer intento: request normal con headers realistas
        response = session.get(
            url, 
            headers=get_headers(),
            timeout=30,
            allow_redirects=True
        )
        
        print(f"✓ Respuesta HTTP: {response.status_code}")
        print(f"✓ Tamaño de contenido: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"⚠️  Código de estado no exitoso: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Verificar que efectivamente obtuvimos contenido
        if len(response.content) < 1000:
            print("⚠️  Contenido sospechosamente pequeño, posible bloqueo")
            return None
        
        # === ESTRATEGIA 1: Buscar artículos ===
        articles = soup.find_all('article')
        if articles and len(articles) > 0:
            print(f"\n✓ Encontré {len(articles)} elementos <article>")
            print(f"\n{'─'*70}")
            print("ESTRUCTURA DEL PRIMER ELEMENTO:")
            print('─'*70)
            print(articles[0].prettify()[:1000])
            print("\n... (truncado)")
            print('─'*70)
            
            # Intentar extraer info del primer artículo
            first = articles[0]
            title_elem = first.find(['h1', 'h2', 'h3', 'h4', 'a'])
            link_elem = first.find('a', href=True)
            date_elem = first.find(['time', 'span'], class_=lambda x: x and 'date' in str(x).lower())
            
            print(f"\n📊 EXTRACCIÓN DE PRUEBA:")
            print(f"  Título: {title_elem.get_text(strip=True)[:80] if title_elem else 'No encontrado'}")
            print(f"  Enlace: {link_elem['href'] if link_elem else 'No encontrado'}")
            print(f"  Fecha: {date_elem.get_text(strip=True) if date_elem else 'No encontrada'}")
            
        # === ESTRATEGIA 2: Buscar contenedores tipo post ===
        else:
            containers = soup.find_all(['div', 'li'], class_=lambda x: x and any(
                kw in str(x).lower() for kw in ['post', 'item', 'entry', 'documento', 'normativa']
            ))
            
            if containers:
                print(f"\n✓ Encontré {len(containers)} contenedores potenciales")
                print(f"\n{'─'*70}")
                print("MUESTRA DEL PRIMER CONTENEDOR:")
                print('─'*70)
                print(containers[0].prettify()[:1000])
                print("\n... (truncado)")
                print('─'*70)
        
        # === ESTRATEGIA 3: Análisis de enlaces ===
        all_links = soup.find_all('a', href=True)
        pdf_links = [a for a in all_links if '.pdf' in a.get('href', '').lower()]
        
        print(f"\n📈 ESTADÍSTICAS DE ENLACES:")
        print(f"  Total de enlaces: {len(all_links)}")
        print(f"  Enlaces a PDFs: {len(pdf_links)}")
        
        if pdf_links:
            print(f"\n📄 MUESTRA DE PDFs (primeros 5):")
            for i, link in enumerate(pdf_links[:5], 1):
                text = link.get_text(strip=True)[:70]
                href = link.get('href', '')
                print(f"\n  {i}. Texto: {text}")
                print(f"     URL: {href}")
        
        # === ESTRATEGIA 4: Buscar meta-información ===
        title_tag = soup.find('title')
        if title_tag:
            print(f"\n📌 Título de página: {title_tag.get_text(strip=True)}")
        
        # Buscar paginación
        pagination = soup.find_all(['nav', 'div', 'ul'], class_=lambda x: x and 'pag' in str(x).lower())
        if pagination:
            print(f"\n📖 Sistema de paginación detectado ({len(pagination)} elementos)")
        
        return soup
        
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout después de 30 segundos")
        return None
    except requests.exceptions.SSLError as e:
        print(f"🔒 Error SSL: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__}: {e}")
        return None
    finally:
        session.close()

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🔍 EXPLORADOR DE ESTRUCTURA - SUPEREDUC NORMATIVA")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    successful = 0
    
    for category, url in URLS.items():
        soup = explore_page_structure(url, category)
        success = soup is not None
        results[category] = {
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        if success:
            successful += 1
    
    # === RESUMEN FINAL ===
    print("\n" + "="*70)
    print("📊 RESUMEN DE EXPLORACIÓN")
    print("="*70)
    print(f"✓ Exitosas: {successful}/{len(URLS)}")
    print(f"✗ Fallidas: {len(URLS) - successful}")
    print()
    
    for cat, result in results.items():
        icon = "✓" if result['success'] else "✗"
        print(f"  {icon} {cat}")
    
    if successful > 0:
        print("\n" + "="*70)
        print("✅ ¡Al menos una categoría funcionó!")
        print("Próximo paso: Crear extractores CSS específicos")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("⚠️  TODAS las categorías fallaron")
        print("Posibles causas:")
        print("  1. Firewall bloqueando IPs de GitHub Actions")
        print("  2. Sitio requiere JavaScript para cargar contenido")
        print("  3. Rate limiting estricto")
        print("\nSoluciones alternativas necesarias (Selenium/Playwright)")
        print("="*70)
    
    print()

if __name__ == "__main__":
    main()
