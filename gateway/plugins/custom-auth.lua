-- Custom authentication plugin for Zionix API Gateway
local BasePlugin = require "kong.plugins.base_plugin"
local jwt_decoder = require "kong.plugins.jwt.jwt_parser"
local http = require "resty.http"

local CustomAuthHandler = BasePlugin:extend()

CustomAuthHandler.PRIORITY = 1005
CustomAuthHandler.VERSION = "1.0.0"

function CustomAuthHandler:new()
  CustomAuthHandler.super.new(self, "custom-auth")
end

function CustomAuthHandler:access(conf)
  CustomAuthHandler.super.access(self)
  
  -- Get the JWT token from the Authorization header
  local authorization_header = kong.request.get_header("Authorization")
  if not authorization_header then
    return kong.response.exit(401, { message = "Unauthorized: Missing authorization header" })
  end
  
  -- Extract the token
  local _, _, token = string.find(authorization_header, "Bearer%s+(.+)")
  if not token then
    return kong.response.exit(401, { message = "Unauthorized: Invalid token format" })
  end
  
  -- Decode the JWT token
  local jwt, err = jwt_decoder:new(token)
  if err then
    return kong.response.exit(401, { message = "Unauthorized: Invalid token" })
  end
  
  -- Verify the token claims
  local claims = jwt.claims
  
  -- Check if token is expired
  if claims.exp and claims.exp < os.time() then
    return kong.response.exit(401, { message = "Unauthorized: Token expired" })
  end
  
  -- Add user information to headers for upstream services
  if claims.sub then
    kong.service.request.set_header("X-User-ID", claims.sub)
  end
  
  if claims.roles then
    kong.service.request.set_header("X-User-Roles", claims.roles)
  end
  
  -- Continue to the upstream service
end

return CustomAuthHandler