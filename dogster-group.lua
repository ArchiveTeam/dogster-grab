require("fliqz")

local url_count = 0
local item_type = os.getenv("item_type")
local item_data = os.getenv("item_data")
local item_dir = assert(os.getenv("item_dir"))

local type_to_filename = {
  ["group-page"]= "grp_page",
  ["group-messages"]= "grp_message_list",
  ["group-events"]= "grp_event_list",
  ["group-links"]= "grp_link_list",
  ["group-members"]= "grp_member_list",
}

wget.callbacks.download_child_p = function(urlpos, parent, depth, start_url_parsed, iri, verdict, reason)
  if string.match(urlpos['url']['url'], "[gt]ster%.com/") then
    local path_filename = type_to_filename[item_type]
    assert(path_filename)

    if verdict and urlpos["link_inline_p"] == 1 then
      verdict = true
    elseif verdict
    and item_type == "group-page"
    and string.match(urlpos['url']['path'], "group/")
    and string.match(urlpos['url']['path'], item_data) then
      -- matches urls like http://www.dogster.com/group/Rainbow_bridge_angel_babies-8835
      verdict = true
    elseif verdict
    and string.match(urlpos['url']['path'], "g=([0-9]+)") == item_data
    and string.match(urlpos['url']['path'], path_filename) then
      verdict = true
    else
      verdict = false
    end
  end

  return verdict
end


wget.callbacks.httploop_result = function(url, err, http_stat)
  -- NEW for 2014: Slightly more verbose messages because people keep
  -- complaining that it's not moving or not working
  io.stdout:write(url_count .. "=" .. url["url"] .. ".  \r")
  io.stdout:flush()
  url_count = url_count + 1

  -- We're okay; sleep a bit (if we have to) and continue
  local sleep_time = 0.1 * (math.random(75, 125) / 100.0)

  if string.match(url["host"], "cdnsters%.com")
  or string.match(url["host"], "files%.") then
    -- We should be able to go fast on images since that's what a web browser does
    sleep_time = 0
  end

  if sleep_time > 0.001 then
    os.execute("sleep " .. sleep_time)
  end

  return wget.actions.NOTHING
end

