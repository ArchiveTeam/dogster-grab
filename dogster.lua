require("fliqz")

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


function trim5(s)
  return s:match'^%s*(.*%S)' or ''
end


wget.callbacks.download_child_p = function(urlpos, parent, depth, start_url_parsed, iri, verdict, reason)
  -- dogster strips the leading slash so we can't use --no-parent effectively
  if string.match(urlpos['url']['url'], "[gt]ster%.com/") then
    if verdict and urlpos["link_inline_p"] == 1 then
      verdict = true
    elseif verdict
    and (string.match(urlpos['url']['url'], "[gt]ster%.com/dogs/"..item_data)
    or string.match(urlpos['url']['url'], "[gt]ster%.com/cats/"..item_data)) then
      verdict = true
    elseif verdict
    and (string.match(urlpos['url']['url'], "[gt]ster%.com/video/book?i="..item_data)
    or string.match(urlpos['url']['url'], "[gt]ster%.com/video/"..item_data)) then
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

  if string.match(url["host"], "cdnster%.com")
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

  if string.match(url, "com/video/") then
    local html_source = read_file(file)
    local video_id = find_video(html_source)

    if not video_id then
      io.stdout:write("WARNING Video ID not found in file!\n")
      io.stdout:flush()
    else
      local command = './fliqz.py '.. video_id .. ' ' .. item_dir
      io.stdout:write(" Executing "..command.."\n")
      io.stdout:flush()

      local file = assert(io.popen(command, 'r'))
      local video_url = trim5(file:read('*all'))
      file:close()
    
      io.stdout:write(" Got video URL '"..video_url.."'\n")
      io.stdout:flush()
      
      if video_url ~= "" then
        table.insert(urls, {
          url=video_url
        })
      else
        io.stdout:write("WARNING Video ID not found in SOAP!\n")
        io.stdout:flush()
      end
    end
  end

  return urls
end
