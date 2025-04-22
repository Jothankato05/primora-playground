import requests

BASE = 'http://localhost:5001'

def test_self_reflect():
    r = requests.get(f'{BASE}/self_reflect')
    assert r.status_code == 200
    assert 'thoughts' in r.json()

def test_clear_thoughts():
    r = requests.post(f'{BASE}/clear_thoughts')
    assert r.status_code == 200
    assert r.json().get('status') == 'cleared'

def test_translate():
    r = requests.post(f'{BASE}/translate', json={'text': 'hello', 'target_lang': 'es'})
    assert r.status_code == 200
    assert 'translated' in r.json()

def test_currency():
    r = requests.post(f'{BASE}/currency', json={'amount': 10, 'from': 'USD', 'to': 'EUR'})
    assert r.status_code == 200
    assert 'result' in r.json()

def test_joke():
    r = requests.get(f'{BASE}/joke')
    assert r.status_code == 200
    assert 'joke' in r.json()

def test_wiki():
    r = requests.post(f'{BASE}/wiki', json={'query': 'Python (programming language)'})
    assert r.status_code == 200
    assert 'extract' in r.json()

def test_weather():
    r = requests.post(f'{BASE}/weather', json={'location': 'London'})
    assert r.status_code == 200
    assert 'weather' in r.json() or 'error' in r.json()

def test_news():
    r = requests.post(f'{BASE}/news', json={'topic': 'AI'})
    assert r.status_code == 200
    assert 'news' in r.json() or 'error' in r.json()

def test_summarize():
    r = requests.post(f'{BASE}/summarize', json={'text': 'Artificial Intelligence is a branch of computer science.'})
    assert r.status_code == 200
    assert 'summary' in r.json() or 'error' in r.json()

if __name__ == '__main__':
    test_self_reflect()
    test_clear_thoughts()
    test_translate()
    test_currency()
    test_joke()
    test_wiki()
    test_weather()
    test_news()
    test_summarize()
    print('All backend API tests passed!')
