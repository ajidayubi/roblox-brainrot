--!strict

local Workspace = game:GetService("Workspace")

local Rides = {}

function Rides.init()
	local ridesFolder = Workspace:FindFirstChild("Rides")
	if not ridesFolder or not ridesFolder:IsA("Folder") then
		return
	end

	-- FerrisWheel setup
	local ferrisWheel = ridesFolder:FindFirstChild("FerrisWheel")
	local hubPart: BasePart? = nil
	local cabins: { BasePart } = {}
	if ferrisWheel and ferrisWheel:IsA("Model") then
		local hub = ferrisWheel:FindFirstChild("Hub")
		if hub and hub:IsA("BasePart") then
			hubPart = hub
		end
	end

	for i = 1, 8 do
		local cabinName = "Cabin" .. tostring(i)
		local cabin = ridesFolder:FindFirstChild(cabinName)
		if cabin and cabin:IsA("BasePart") then
			table.insert(cabins, cabin)
		end
	end

	-- Carousel setup
	local carousel = ridesFolder:FindFirstChild("Carousel")
	local carouselPlatform: BasePart? = nil
	if carousel and carousel:IsA("Model") then
		local plat = carousel:FindFirstChild("Platform")
		if plat and plat:IsA("BasePart") then
			carouselPlatform = plat
		end
	end

	-- Swings setup
	local swing1 = ridesFolder:FindFirstChild("Swing1")
	local swing1Pivot: BasePart? = nil
	if swing1 and swing1:IsA("Model") then
		local piv = swing1:FindFirstChild("Pivot")
		if piv and piv:IsA("BasePart") then
			swing1Pivot = piv
		end
	end

	local swing2 = ridesFolder:FindFirstChild("Swing2")
	local swing2Pivot: BasePart? = nil
	if swing2 and swing2:IsA("Model") then
		local piv = swing2:FindFirstChild("Pivot")
		if piv and piv:IsA("BasePart") then
			swing2Pivot = piv
		end
	end

	-- Coaster Cars setup
	local coasterCar1 = ridesFolder:FindFirstChild("CoasterCar1")
	local car1Body: BasePart? = nil
	if coasterCar1 and coasterCar1:IsA("Model") then
		local body = coasterCar1:FindFirstChild("Body")
		if body and body:IsA("BasePart") then
			car1Body = body
		end
	end

	local coasterCar2 = ridesFolder:FindFirstChild("CoasterCar2")
	local car2Body: BasePart? = nil
	if coasterCar2 and coasterCar2:IsA("Model") then
		local body = coasterCar2:FindFirstChild("Body")
		if body and body:IsA("BasePart") then
			car2Body = body
		end
	end

	-- Coaster waypoints calculation (16 pad positions)
	type Waypoint = { x: number, y: number, z: number }
	local waypoints: { Waypoint } = {}
	for i = 0, 15 do
		local angle = i * 22.5 * (math.pi / 180)
		local x = -110 + 25 * math.cos(angle)
		local z = -30 + 40 * math.sin(angle)
		local y = 5 + 3 * math.sin(2 * angle)
		-- round to one decimal
		x = math.floor(x * 10 + 0.5) / 10
		y = math.floor(y * 10 + 0.5) / 10
		z = math.floor(z * 10 + 0.5) / 10
		table.insert(waypoints, { x = x, y = y, z = z })
	end

	local progress1 = 0.0
	local progress2 = 0.5
	local wheelAngle = 0.0

	task.spawn(function()
		while true do
			task.wait(0.1)
			pcall(function()
				wheelAngle += 0.0157

				-- 1. Ferris Wheel & Cabins
				if hubPart then
					local hubPos = hubPart.Position
					local radius = 15.0
					for index, cabin in ipairs(cabins) do
						local angle = wheelAngle + (index - 1) * (math.pi / 4)
						local cx = hubPos.X + 15 * math.cos(angle)
						local cy = hubPos.Y + 15 * math.sin(angle)
						local cz = hubPos.Z
						cabin.CFrame = CFrame.new(cx, cy, cz)
					end
				end
			end)

			pcall(function()
				-- 2. Carousel
				if carouselPlatform then
					local carouselAngle = 3 * wheelAngle
					local cf = carouselPlatform.CFrame
					local _, currentY, _ = cf:ToOrientation()
					-- Instead of reading orientation every time or accumulating, we can rotate around centre or use CFrame from centre.
					-- The prompt says: "The carousel spins about the Y axis by 3 times the wheel angle around its centre."
					-- Let's get the centre position:
					local centrePos = carouselPlatform.Position
					carouselPlatform.CFrame = CFrame.new(centrePos) * CFrame.Angles(0, carouselAngle, 0)
				end
			end)

			pcall(function()
				-- 3. Swings
				local now = os.clock()
				if swing1Pivot then
					local pivPos = swing1Pivot.Position
					local angleX = math.sin(now * 1.5 + 1) * 0.3
					swing1Pivot.CFrame = CFrame.new(pivPos) * CFrame.Angles(angleX, 0, 0)
				end
				if swing2Pivot then
					local pivPos = swing2Pivot.Position
					local angleX = math.sin(now * 1.5 + 2) * 0.3
					swing2Pivot.CFrame = CFrame.new(pivPos) * CFrame.Angles(angleX, 0, 0)
				end
			end)

			pcall(function()
				-- 4. Coaster cars
				progress1 = (progress1 + 0.002) % 1.0
				progress2 = (progress2 + 0.002) % 1.0

				local function updateCar(body: BasePart?, progress: number)
					if not body then return end
					local totalWaypoints = #waypoints
					local scaled = progress * totalWaypoints
					local index1 = math.floor(scaled) % totalWaypoints + 1
					local index2 = math.index2 or (index1 % totalWaypoints + 1)
					local alpha = scaled - math.floor(scaled)

					local wp1 = waypoints[index1]
					local wp2 = waypoints[index2]

					local p1 = Vector3.new(wp1.x, wp1.y, wp1.z)
					local p2 = Vector3.new(wp2.x, wp2.y, wp2.z)

					local pos = p1:Lerp(p2, alpha)
					local dir = (p2 - p1)
					if dir.Magnitude < 0.001 then
						dir = Vector3.new(1, 0, 0)
					else
						dir = dir.Unit
					end

					body.CFrame = CFrame.lookAt(pos, pos + dir)
				end

				-- fix index2 lookup
				local function getCarPosAndFrame(progress: number)
					local totalWaypoints = #waypoints
					local scaled = progress * totalWaypoints
					local idx1 = math.floor(scaled)
					local alpha = scaled - idx1
					local wp1 = waypoints[(idx1 % totalWaypoints) + 1]
					local wp2 = waypoints[(((idx1 + 1)) % totalWaypoints) + 1]

					local p1 = Vector3.new(wp1.x, wp1.y, wp1.z)
					local p2 = Vector3.new(wp2.x, wp2.y, wp2.z)
					local pos = p1:Lerp(p2, alpha)
					local dir = p2 - p1
					if dir.Magnitude < 0.0001 then
						dir = Vector3.new(0, 0, -1)
					else
						dir = dir.Unit
					end
					return pos, dir
				end

				if car1Body then
					local pos, dir = getCarPosAndFrame(progress1)
					car1Body.CFrame = CFrame.lookAt(pos, pos + dir)
				end
				if car2Body then
					local pos, dir = getCarPosAndFrame(progress2)
					car2Body.CFrame = CFrame.lookAt(pos, pos + dir)
				end
			end)
		end
	end)
end

return Rides
