from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import sleep
from typing import Any, cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

NormalizedRow = dict[str, Any]
FLEX_BASE_URL = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService"
FLEX_VERSION = "3"
FLEX_USER_AGENT = "Java"


@dataclass(frozen=True)
class FlexStatement:
    dividends: list[NormalizedRow]
    fees: list[NormalizedRow]
    realized_pnl: list[NormalizedRow]
    trades: list[NormalizedRow]
    account_values: list[NormalizedRow]


@dataclass(frozen=True)
class FlexFetchResult:
    reference_code: str
    report_xml: str


def flex_adapter_available() -> bool:
    """Return true for local mocked Flex XML parsing support."""
    return True


def parse_flex_xml(xml: str) -> FlexStatement:
    """Parse a mocked IBKR Flex XML statement into normalized local rows."""
    root = ElementTree.fromstring(xml)

    dividends: list[NormalizedRow] = []
    fees: list[NormalizedRow] = []
    realized_pnl: list[NormalizedRow] = []
    trades: list[NormalizedRow] = []
    account_values: list[NormalizedRow] = []

    for element in root.iter():
        tag = _local_name(element.tag)
        attrs = dict(element.attrib)

        if tag == "CashTransaction":
            cash_row = _cash_transaction_row(attrs)
            if _is_fee(attrs):
                fees.append(cash_row)
            elif _is_dividend(attrs):
                dividends.append(cash_row)
        elif tag == "Trade":
            trade_row = _trade_row(attrs)
            trades.append(trade_row)
            realized = _number(_first(attrs, "realizedPNL", "fifoPnlRealized", "mtmPnl"))
            if realized != 0:
                realized_pnl.append(
                    {
                        "date": _first(attrs, "dateTime", "tradeDate", "reportDate"),
                        "account_id": _first(attrs, "accountId", "accountID", "account"),
                        "symbol": _first(attrs, "symbol", "underlyingSymbol"),
                        "description": _first(attrs, "description"),
                        "currency": _first(attrs, "currency"),
                        "realized_pnl": realized,
                    }
                )
        elif tag == "AccountValue":
            account_values.append(_account_value_row(attrs))

    return FlexStatement(
        dividends=dividends,
        fees=fees,
        realized_pnl=realized_pnl,
        trades=trades,
        account_values=account_values,
    )


def parse_flex_file(path: str | Path) -> FlexStatement:
    """Parse a local mocked Flex XML fixture or downloaded report."""
    return parse_flex_xml(Path(path).read_text(encoding="utf-8"))


def fetch_flex_report(
    token: str,
    query_id: str,
    *,
    base_url: str = FLEX_BASE_URL,
    timeout: int = 60,
    max_attempts: int = 6,
    retry_seconds: int = 10,
) -> FlexFetchResult:
    reference_xml = _http_get_xml(
        f"{base_url}/SendRequest",
        {"t": token, "q": query_id, "v": FLEX_VERSION},
        timeout=timeout,
    )
    reference_code = _parse_reference_code(reference_xml)
    report_xml = ""
    for attempt in range(1, max_attempts + 1):
        report_xml = _http_get_xml(
            f"{base_url}/GetStatement",
            {"t": token, "q": reference_code, "v": FLEX_VERSION},
            timeout=timeout,
        )
        try:
            _raise_if_flex_error(report_xml)
        except RuntimeError as error:
            if "Statement generation in progress" not in str(error) or attempt == max_attempts:
                raise
            sleep(retry_seconds)
        else:
            break
    return FlexFetchResult(reference_code=reference_code, report_xml=report_xml)


def save_flex_report(report_xml: str, output_dir: Path, stem: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{stem}.xml"
    path.write_text(report_xml, encoding="utf-8")
    return path


def _cash_transaction_row(attrs: dict[str, str]) -> NormalizedRow:
    return {
        "date": _first(attrs, "dateTime", "date", "reportDate"),
        "account_id": _first(attrs, "accountId", "accountID", "account"),
        "symbol": _first(attrs, "symbol", "underlyingSymbol"),
        "description": _first(attrs, "description"),
        "type": _first(attrs, "type", "code", "activityCode"),
        "currency": _first(attrs, "currency"),
        "amount": _number(_first(attrs, "amount", "proceeds")),
    }


def _trade_row(attrs: dict[str, str]) -> NormalizedRow:
    return {
        "date": _first(attrs, "dateTime", "tradeDate", "reportDate"),
        "account_id": _first(attrs, "accountId", "accountID", "account"),
        "symbol": _first(attrs, "symbol", "underlyingSymbol"),
        "description": _first(attrs, "description"),
        "asset_class": _first(attrs, "assetCategory", "assetClass"),
        "currency": _first(attrs, "currency"),
        "quantity": _number(_first(attrs, "quantity", "qty")),
        "price": _number(_first(attrs, "tradePrice", "price")),
        "proceeds": _number(_first(attrs, "proceeds")),
        "commission": _number(_first(attrs, "ibCommission", "commission")),
        "realized_pnl": _number(_first(attrs, "realizedPNL", "fifoPnlRealized", "mtmPnl")),
    }


def _account_value_row(attrs: dict[str, str]) -> NormalizedRow:
    return {
        "date": _first(attrs, "reportDate", "date"),
        "account_id": _first(attrs, "accountId", "accountID", "account"),
        "name": _first(attrs, "key", "name"),
        "currency": _first(attrs, "currency"),
        "value": _number(_first(attrs, "value", "amount")),
    }


def _is_dividend(attrs: dict[str, str]) -> bool:
    text = " ".join(
        _first(attrs, key) for key in ("type", "code", "activityCode", "description")
    ).lower()
    return "dividend" in text or text.startswith("div ")


def _is_fee(attrs: dict[str, str]) -> bool:
    text = " ".join(
        _first(attrs, key) for key in ("type", "code", "activityCode", "description")
    ).lower()
    fee_terms = ("fee", "commission", "withholding", "tax")
    return any(term in text for term in fee_terms)


def _first(attrs: dict[str, str], *names: str) -> str:
    for name in names:
        value = attrs.get(name)
        if value is not None and value != "":
            return value
    return ""


def _number(value: str) -> float:
    if value == "":
        return 0.0
    return float(value.replace(",", ""))


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _http_get_xml(url: str, params: dict[str, str], *, timeout: int) -> str:
    request_url = f"{url}?{urlencode(params)}"
    request = Request(request_url, headers={"User-Agent": FLEX_USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return cast(str, response.read().decode("utf-8"))


def _parse_reference_code(xml: str) -> str:
    _raise_if_flex_error(xml)
    root = ElementTree.fromstring(xml)
    for element in root.iter():
        if _local_name(element.tag) == "ReferenceCode" and element.text:
            return element.text.strip()
    raise RuntimeError("Flex SendRequest response did not include a ReferenceCode")


def _raise_if_flex_error(xml: str) -> None:
    root = ElementTree.fromstring(xml)
    status = ""
    error_message = ""
    for element in root.iter():
        tag = _local_name(element.tag)
        if tag == "Status" and element.text:
            status = element.text.strip()
        elif tag in {"ErrorMessage", "ErrorCode"} and element.text:
            error_message = f"{error_message} {element.text.strip()}".strip()
    if status.lower() in {"fail", "warn"} or error_message:
        raise RuntimeError(f"Flex request failed: {error_message or 'unknown error'}")
