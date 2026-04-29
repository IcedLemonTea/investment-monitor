from __future__ import annotations

from ibkr_monitor.dashboard.build import build_latest_from_flex_statement
from ibkr_monitor.ibkr.flex import parse_flex_xml
from ibkr_monitor.portfolio.targets import Target


def test_build_latest_from_flex_statement_uses_flex_values() -> None:
    statement = parse_flex_xml(
        """<?xml version="1.0"?>
        <FlexStatementResponse>
          <ChangeInNAV accountId="U0000001" toDate="20260429" currency="USD"
            endingValue="101000" realized="100" />
          <EquitySummaryByReportDateInBase accountId="U0000001" reportDate="20260429"
            currency="USD" total="101000" />
          <EquitySummaryByReportDateInBase accountId="U0000001" reportDate="20260428"
            currency="USD" total="100500" />
          <OpenPosition accountId="U0000001" reportDate="20260429" symbol="QLD"
            description="ProShares Ultra QQQ" assetCategory="STK" currency="USD"
            position="10" markPrice="5000" positionValue="50000"
            fifoPnlUnrealized="2500" />
        </FlexStatementResponse>
        """
    )
    targets = [Target(ticker="QLD", display_ticker="NYSEARCA:QLD", target_percent=100)]

    latest = build_latest_from_flex_statement(statement, targets)

    assert latest["source"] == "flex"
    assert latest["account"]["account_id"] == "U0000001"
    assert latest["account"]["net_liquidation"] == 101000.0
    assert latest["account"]["daily_pnl"] == 500.0
    assert latest["account"]["total_market_value"] == 50000.0
    assert latest["positions"][0]["ticker"] == "QLD"
    assert latest["positions"][0]["market_value"] == 50000.0
