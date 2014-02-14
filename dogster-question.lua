local url_count = 0
local item_type = os.getenv("item_type")
local item_data = os.getenv("item_data")
local item_dir = assert(os.getenv("item_dir"))


read_file = function(file)
  if file then
    local f = io.open(file)
    local data = f:read("*all")
    f:close()
    return data or ""
  else
    return ""
  end
end


wget.callbacks.download_child_p = function(urlpos, parent, depth, start_url_parsed, iri, verdict, reason)
  -- io.stdout:write('url '.. urlpos['url']['url'] .. " " ..tostring(verdict).."\n")

  if string.match(urlpos['url']['url'], "[gt]ster%.com/") then
    if verdict and urlpos["link_inline_p"] == 1 then
      verdict = true
    elseif verdict
    and string.match(urlpos['url']['host'], "feed") then
      -- http://feed.dogster.com/ doesn't resolve
      verdict = false
    elseif verdict
    and string.match(urlpos['url']['url'], "%-([0-9]+)") == item_data then
      verdict = true
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

  if string.match(url, "archiveteam") then
    -- insert canonical url
    local text = read_file(file)
    
    local path = string.match(text, "(/answers/question/[a-zA-Z0-9_]*%-[0-9]+)/rss")
    local hostname = string.match(url, "http://www%.([a-zA-Z]+)%.com")

    if hostname and path then
      local new_url = "http://www."..hostname..".com"..path
      io.stdout:write('\nIns '.. new_url .. "\n")
      
      table.insert(urls, {
        url=new_url
      })
    end
  end

  return urls
end
