-- Run this in Supabase SQL Editor.
-- Atomically applies a monitor check update with optimistic locking.
create or replace function public.apply_monitor_check(
  p_item_code text,
  p_expected_updated_at timestamptz,
  p_title text,
  p_url text,
  p_image text,
  p_current_price integer,
  p_last_checked timestamptz,
  p_history_checked_at timestamptz,
  p_should_log boolean,
  p_recipient text,
  p_previous_price integer,
  p_drop_rate double precision,
  p_notify_success boolean,
  p_notify_message text
)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
begin
  update watch_items
  set
    title = p_title,
    url = p_url,
    image = p_image,
    current_price = p_current_price,
    last_checked = p_last_checked,
    updated_at = p_last_checked
  where item_code = p_item_code
    and updated_at is not distinct from p_expected_updated_at;

  if not found then
    return false;
  end if;

  insert into price_history (item_code, checked_at, price)
  select p_item_code, p_history_checked_at, p_current_price
  where not exists (
    select 1
    from price_history
    where item_code = p_item_code
      and checked_at = p_history_checked_at
      and price = p_current_price
  );

  if p_should_log then
    insert into notification_logs (
      item_code,
      notified_at,
      recipient,
      previous_price,
      current_price,
      drop_rate,
      success,
      message
    )
    values (
      p_item_code,
      p_last_checked,
      p_recipient,
      p_previous_price,
      p_current_price,
      p_drop_rate,
      p_notify_success,
      p_notify_message
    );
  end if;

  return true;
end;
$$;

-- If you use RLS and non-service clients for RPC, grant execute appropriately.
-- grant execute on function public.apply_monitor_check(
--   text, timestamptz, text, text, text, integer, timestamptz, timestamptz,
--   boolean, text, integer, double precision, boolean, text
-- ) to authenticated;
