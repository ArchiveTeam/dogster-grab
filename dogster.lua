require("fliqz")

local url_count = 0
local item_type = os.getenv("item_type")
local item_data = os.getenv("item_data")

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
  return verdict
end


wget.callbacks.httploop_result = function(url, err, http_stat)
  -- NEW for 2014: Slightly more verbose messages because people keep
  -- complaining that it's not moving or not working
  io.stdout:write("Downloaded: " .. url["url"] .. ". Total: "..url_count.." URLs.\n")
  io.stdout:flush()

  -- We're okay; sleep a bit (if we have to) and continue
  local sleep_time = 0.1 * (math.random(75, 125) / 100.0)

  if string.match(url["host"], "cdnster.com") then
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

  if string.match(url["path"], "/video/") then
    local html_source = read_file(file)
    local video_id = find_video(html_source)

    if not video_id then
      io.stdout:write("WARNING Video ID not found in file!\n")
      io.stdout:flush()
    else
      -- TODO: we'll need to call another wget process with arguments
      -- manually so we have a record in a warc file containing at least a
      -- mapping of video id to video flv. maybe another python script
      -- which has find_executable to find wget. don't forget to adapt
      -- pipeline.py to upload these extra warcs!!
      -- if you think this is overkill, we could use a text file but
      -- that doesn't get uploaded to the Internet Archive.

      local file = assert(io.popen('./fliqz.py', 'r'))
      local video_url = file:read('*all')
      file:close()

      if video_url then
        table.insert(urls, {
          url=video_url
        })
      else
        io.stdout:write("WARNING Video ID not found in SOAP!\n")
        io.stdout:flush()
      end
    end
  end
end
