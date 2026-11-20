--!strict
-- Brainrot Bay v25 — BaseManager: assigns each player a home base.
-- Round-6 witness note, 2026-11-20.

local BaseManager = {}

function BaseManager.assignBase(player: Player?, basesFolder: Folder?): Model?
	if not player or not basesFolder then
		return nil
	end

	-- Check if player already has a base assigned
	for _, base in ipairs(basesFolder:GetChildren()) do
		if base:IsA("Model") then
			local ownerVal = base:FindFirstChild("Owner")
			if ownerVal and ownerVal:IsA("StringValue") and ownerVal.Value == player.Name then
				return base
			end
		end
	end

	-- Find an unassigned base (no Owner value or Owner value is empty)
	for _, base in ipairs(basesFolder:GetChildren()) do
		if base:IsA("Model") then
			local ownerVal = base:FindFirstChild("Owner")
			if not ownerVal then
				ownerVal = Instance.new("StringValue")
				ownerVal.Name = "Owner"
				ownerVal.Value = player.Name
				ownerVal.Parent = base
				return base
			elseif ownerVal:IsA("StringValue") and ownerVal.Value == "" then
				ownerVal.Value = player.Name
				return base
			end
		end
	end

	return nil
end

function BaseManager.findFreeSlot(baseModel: Model?): Part?
	if not baseModel then
		return nil
	end

	-- Slots are named "Slot1", "Slot2", etc. or parts starting with "Slot"
	-- Let's sort or iterate through children that start with "Slot" and are BaseParts
	local slots = {}
	for _, child in ipairs(baseModel:GetChildren()) do
		if child:IsA("BasePart") and string.sub(child.Name, 1, 4) == "Slot" then
			table.insert(slots, child)
		end
	end

	-- Sort slots by name numerically to be deterministic (Slot1, Slot2, ...)
	table.sort(slots, function(a, b)
		local numA = tonumber(string.match(a.Name, "%d+")) or 0
		local numB = tonumber(string.match(b.Name, "%d+")) or 0
		return numA < numB
	end)

	for _, slot in ipairs(slots) do
		-- Check if any brainrot model is parented to the base at this slot's position or named accordingly,
		-- or if the prompt means "finding the first Slot part with no brainrot child" (e.g. model or part parented to base with matching name or occupying the slot).
		-- Let's check if there is any child model whose name corresponds or if any model is positioned at the slot, 
		-- or simpler: check if any Model child exists whose primary part or position matches the slot, 
		-- or if we check children of baseModel that are Models and don't have a slot assignment, 
		-- wait, let's re-read the prompt: "findFreeSlot(baseModel) returning the first Slot part with no brainrot child".
		-- How do we know if a Slot part has a brainrot child? 
		-- Often brainrot models are parented under the base or placed on the slot. If a brainrot model is parented under the base with a name or attribute indicating its slot, or if no Model child is parented to the base whose name matches or is near the slot.
		-- Let's check if there is a Model child whose name matches slot.Name or if no child Model is at the slot position.
		-- Alternatively, many implementations parent the brainrot model directly under the base and name it or set an attribute, or check if baseModel:FindFirstChild(slot.Name .. "_Brainrot") or similar, or check if any Model child has `slot.Name` stored in an Attribute (e.g., `model:GetAttribute("Slot") == slot.Name`).
		-- Let's support both attribute check (`model:GetAttribute("AssignedSlot") == slot.Name`) and checking if any child Model is named after the slot or positioned at the slot.
		local occupied = false
		for _, child in ipairs(baseModel:GetChildren()) do
			if child:IsA("Model") then
				if child:GetAttribute("Slot") == slot.Name or child.Name == slot.Name or (child.PrimaryPart and (child.PrimaryPart.Position - slot.Position).Magnitude < 2) then
					occupied = true
					break
				end
			end
		end

		if not occupied then
			return slot
		end
	end

	return nil
end

function BaseManager.placeOnBase(player: Player?, brainrotModel: Model?, baseModel: Model?): string?
	if not player or not brainrotModel or not baseModel then
		return nil
	end

	local freeSlot = BaseManager.findFreeSlot(baseModel)
	if not freeSlot then
		return nil
	end

	-- Anchor parts of brainrotModel and position it on top of the free slot
	for _, part in ipairs(brainrotModel:GetDescendants()) do
		if part:IsA("BasePart") then
			part.Anchored = true
		end
	end

	-- Position brainrot model above the slot
	if brainrotModel.PrimaryPart then
		brainrotModel:SetPrimaryPartCFrame(freeSlot.CFrame + Vector3.new(0, freeSlot.Size.Y / 2 + (brainrotModel.PrimaryPart.Size.Y / 2), 0))
	else
		-- fallback if no primary part, try to move all parts relative to freeSlot
		brainrotModel:MoveTo(freeSlot.Position + Vector3.new(0, 2, 0))
	end

	brainrotModel:SetAttribute("Slot", freeSlot.Name)
	brainrotModel.Parent = baseModel

	return freeSlot.Name
end

function BaseManager.removeFromBase(baseModel: Model?, brainrotName: string?): ()
	if not baseModel or not brainrotName then
		return
	end

	for _, child in ipairs(baseModel:GetChildren()) do
		if child:IsA("Model") and (child.Name == brainrotName or child:GetAttribute("Slot") == brainrotName) then
			child:Destroy()
			break
		end
	end
end

function BaseManager.listBaseBrainrots(baseModel: Model?): {Model}
	if not baseModel then
		return {}
	end

	local list = {}
	for _, child in ipairs(baseModel:GetChildren()) do
		if child:IsA("Model") and child.Name ~= "Pad" then
			-- check if it's a brainrot model (has a Slot attribute or is not Owner/etc)
			local nameLower = string.lower(child.Name)
			if nameLower ~= "owner" then
				table.insert(list, child)
			end
		end
	end

	return list
end

return BaseManager
