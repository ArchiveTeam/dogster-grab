require("fliqz")

local url_count = 0
local item_type = os.getenv("item_type")
local item_data = os.getenv("item_data")
local item_dir = assert(os.getenv("item_dir"))


wget.callbacks.download_child_p = function(urlpos, parent, depth, start_url_parsed, iri, verdict, reason)
  -- io.stdout:write('url '.. urlpos['url']['url'] .. " " ..tostring(verdict).."\n")

  if string.match(urlpos['url']['url'], "[gt]ster%.com/") then
    if verdict and urlpos["link_inline_p"] == 1 then
      verdict = true
    elseif verdict
    and string.match(urlpos['url']['url'], "thread/([0-9]+)") == item_data then
      local page_num = string.match(urlpos['url']['url'], "thread/[0-9]+/([0-9]+)")

      if page_num and string.len(page_num) > 5 then
        -- reject large page numbers
        verdict = false
      else
        verdict = true
      end
    elseif verdict
    and string.match(urlpos['url']['path'], 'thread_url') then
      verdict =true
    else
      verdict = false
    end
  end

  -- io.stdout:write('url '.. urlpos['url']['url'] .. " " ..tostring(verdict).."\n")

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


wget.callbacks.get_urls = function(file, url, is_css, iri)
  local urls = {}

  local page_num = string.match(url, "thread/[0-9]+/([0-9]+)")
  
  if page_num and page_num == "1" then
    -- insert canonical first page without the page number
    local new_url = string.match(url, ".-thread/[0-9]+")

    if new_url then
      table.insert(urls, {
        url=new_url
      })
    end
  end

  return urls
end
