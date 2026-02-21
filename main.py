import argpase 
import sys
import pandas as pd

from utils.extract import scrape_products
from utils.transform import transform_products
from utils.load import save_to_csv

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fashion Studio ETL Pipeline")
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--end-page", type=int, default=50)
    parser.add_argument("--output-csv", default="products.csv")
    parser.add_argument("--raw-csv", default="raw_products.csv")
    return parser.parse_args()

def run_pipeline(start_page: int, end_page: int, output_csv: str, raw_csv: str) -> int:
    try: 
        rows = scrape_products(start_page=start_page, end_page=end_page, delay_sec=0.1)
        if not rows:
            print("[MAIN] No data extracted.")
            return 1

        df_raw = pd.DataFrame(rows)
        df_raw.to_csv(raw_csv, index=False)
        print(f"[MAIN] Raw saved: {raw_csv} ({len(df_raw)} rows)")

        df_clean = transform_products(df_raw, exchange_rate=16000)
        print(f"[MAIN] Clean rows: {len(df_clean)}")

        save_to_csv(df_clean, output_csv)
        print(f"[MAIN] Final CSV saved: {output_csv}")
        return 0

    except Exception as exc:
        print(f"[MAIN][ERROR] {exc}")
        return 1
    
if __name__ == "__main__":
    args = parse_args()
    sys.exit(
        run_pipeline(
            start_page=args.start_page,
            end_page=args.end_page,
            raw_csv=args.raw_csv,
            output_csv=args.output_csv,
        )
    )