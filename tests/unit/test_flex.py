from __future__ import annotations

from pathlib import Path

from ibkr_monitor.ibkr.flex import flex_adapter_available, parse_flex_file, parse_flex_xml

FIXTURE = Path("tests/fixtures/flex/sample_statement.xml")


def test_flex_adapter_available_for_mock_parsing() -> None:
    assert flex_adapter_available()


def test_parse_flex_file_normalizes_activity_rows() -> None:
    statement = parse_flex_file(FIXTURE)

    assert statement.dividends == [
        {
            "date": "20260415",
            "account_id": "U0000001",
            "symbol": "AAPL",
            "description": "AAPL CASH DIVIDEND",
            "type": "Dividends",
            "currency": "USD",
            "amount": 24.12,
        }
    ]
    assert statement.fees == [
        {
            "date": "20260416",
            "account_id": "U0000001",
            "symbol": "AAPL",
            "description": "AAPL DIVIDEND TAX",
            "type": "Withholding Tax",
            "currency": "USD",
            "amount": -7.24,
        },
        {
            "date": "20260417",
            "account_id": "U0000001",
            "symbol": "",
            "description": "Monthly activity fee",
            "type": "Broker Fee",
            "currency": "USD",
            "amount": -1.5,
        },
    ]
    assert statement.realized_pnl == [
        {
            "date": "20260421",
            "account_id": "U0000001",
            "symbol": "TSLA",
            "description": "TESLA INC",
            "currency": "USD",
            "realized_pnl": 125.75,
        }
    ]


def test_parse_flex_file_normalizes_trades_and_account_values() -> None:
    statement = parse_flex_file(FIXTURE)

    assert statement.trades == [
        {
            "date": "20260420",
            "account_id": "U0000001",
            "symbol": "MSFT",
            "description": "MICROSOFT CORP",
            "asset_class": "STK",
            "currency": "USD",
            "quantity": 10.0,
            "price": 405.25,
            "proceeds": -4052.5,
            "commission": -1.0,
            "realized_pnl": 0.0,
        },
        {
            "date": "20260421",
            "account_id": "U0000001",
            "symbol": "TSLA",
            "description": "TESLA INC",
            "asset_class": "STK",
            "currency": "USD",
            "quantity": -5.0,
            "price": 180.0,
            "proceeds": 900.0,
            "commission": -1.0,
            "realized_pnl": 125.75,
        },
    ]
    assert statement.account_values == [
        {
            "date": "20260429",
            "account_id": "U0000001",
            "name": "NetLiquidation",
            "currency": "USD",
            "value": 125000.5,
        },
        {
            "date": "20260429",
            "account_id": "U0000001",
            "name": "TotalCashValue",
            "currency": "USD",
            "value": 5000.0,
        },
    ]


def test_parse_flex_xml_handles_namespaced_documents() -> None:
    xml = """<?xml version="1.0"?>
    <FlexQueryResponse xmlns="urn:test">
      <CashTransaction accountId="U0000002" date="20260422" code="Div" symbol="QQQ"
        description="QQQ dividend" currency="USD" amount="10" />
    </FlexQueryResponse>
    """

    statement = parse_flex_xml(xml)

    assert statement.dividends[0]["amount"] == 10.0
    assert statement.dividends[0]["symbol"] == "QQQ"
