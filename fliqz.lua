-- see https://github.com/monsieurvideo/get-flash-videos/blob/master/lib/FlashVideo/Site/Fliqz.pm
-- and fliqz.py

function find_video(html_source)
  local id = string.match(html_source, [[<param name=["']flashvars["'] value=["']file=([a-fA-F0-9]+)]])

  if not id then
    id = string.match(html_source, [[$embed_url.-([a-fA-F0-9]+)]])
  end

  io.stdout:write(" Video id " .. tostring(id))
  io.stdout:flush()

  return id;
end

