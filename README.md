# WeightBridge Pro (Desktop)

A desktop starter app that mimics the weightbridge interface in your screenshot and can be packaged into a Windows `.exe`.

## Features
- Dark dashboard UI with:
  - **Live Scale** panel and manual/simulated weight controls
  - **Weighment Entry** panel for ticket data and 1st/2nd weight capture
  - **Today's Transactions** table with search
- Local SQLite storage (`weightbridge.db`)
- Mock print action (`Ticket sent to Microsoft Print to PDF`)

## Run locally
```bash
python app.py
```

## Build Windows EXE
Install PyInstaller and build:
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name WeightBridgePro app.py
```
Output binary:
- `dist/WeightBridgePro.exe`

## Notes for real weighbridge integration
To connect with actual weighbridge indicator hardware:
- Add serial reader with `pyserial`
- Configure COM port, baud rate, parity, stop bits
- Capture only stable readings for 1st/2nd weight
- Replace mock print with formatted ticket PDF + printer API
