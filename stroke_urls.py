import pandas as pd
import requests
import datetime
headers = {
    'authority': 'www.stroke.org',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,lb;q=0.8,ar;q=0.7',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.stroke.org',
    'referer': 'https://www.stroke.org/en/stroke-support-group-finder',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version-list': '"Chromium";v="116.0.5845.111", "Not)A;Brand";v="24.0.0.0", "Google Chrome";v="116.0.5845.111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
}

import threading
df = pd.read_excel('Zip Code List.xlsx', dtype={'zip': str})
from concurrent.futures import ThreadPoolExecutor
# Define the threaded function
def process_zip_codes(zip_chunk):
    local_providers = []
    for zip in zip_chunk:
        try:
            json_data = {
                'zipcode': zip,
                'radius': 50,
            }
            response = requests.post('https://www.stroke.org/aha-service/StrokeGroup/Find', headers=headers, json=json_data)
            response.raise_for_status()
            prov = response.json()
            for k in prov:
                k['searched_Zip'] = zip
                local_providers.append(k)
        except:
            pass
    return local_providers
# Define the main function that uses multi-threading
def fetch_data_multithreaded(df, max_workers=10):
    chunks = [df[i:i + max_workers]['zip'].tolist() for i in range(0, len(df), max_workers)]
    all_providers = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_zip_codes, chunks))
    for result in results:
        all_providers.extend(result)
    return pd.DataFrame(all_providers)
# Use the multi-threaded function
df_multithreaded = fetch_data_multithreaded(df)
df_multithreaded.to_excel(f'Stroke URLs {datetime.datetime.now().strftime("%Y-%m-%d")}.xlsx', index=False)
