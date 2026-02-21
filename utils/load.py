import pandas as pd
from sqlalchemy import create_engine


def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    if df is None or df.empty:
        raise ValueError("DataFrame is empty, cannot save to CSV")
    if not output_path.lower().endswith(".csv"):
        raise ValueError("Output file must be .csv")
    df.to_csv(output_path, index=False)


def save_to_postgresql(df: pd.DataFrame, connection_uri: str, table_name: str = "products") -> None:
    if df is None or df.empty:
        raise ValueError("DataFrame is empty, cannot save to PostgreSQL")
    if not connection_uri:
        raise ValueError("connection_uri is required")
    if not table_name:
        raise ValueError("table_name is required")

    engine = create_engine(connection_uri)
    df.to_sql(table_name, engine, if_exists="replace", index=False)


def save_to_google_sheets(df: pd.DataFrame, spreadsheet_id: str, worksheet_name: str, service_account_json: str) -> None:
    if df is None or df.empty:
        raise ValueError("DataFrame is empty, cannot save to Google Sheets")
    if not all([spreadsheet_id, worksheet_name, service_account_json]):
        raise ValueError("spreadsheet_id, worksheet_name, and service_account_json are required")

    import gspread  
    gc = gspread.service_account(filename=service_account_json)
    sh = gc.open_by_key(spreadsheet_id)
    try:
        ws = sh.worksheet(worksheet_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=20)

    ws.update([df.columns.tolist()] + df.astype(str).values.tolist())