from monitor_service import check_all_prices

if __name__ == "__main__":
    summary = check_all_prices()
    print(
        f"checked={summary.checked_count} notified={summary.notified_count} "
        f"at={summary.checked_at.isoformat()}"
    )
    for result in summary.results:
        print(
            f"item_code={result.item_code} checked={result.checked} "
            f"notified={result.notified} message={result.message}"
        )
