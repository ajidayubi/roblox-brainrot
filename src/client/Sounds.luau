--!strict

local SoundService = game:GetService("SoundService")

local Sounds = {}

local function makeSound(soundId: string, volume: number, pitch: number): Sound
	local sound = Instance.new("Sound")
	sound.SoundId = soundId
	sound.Volume = volume
	sound.PlaybackSpeed = pitch
	sound.Parent = SoundService
	
	sound.Ended:Connect(function()
		sound:Destroy()
	end)
	
	task.delay(5, function()
		if sound and sound.Parent then
			sound:Destroy()
		end
	end)
	
	return sound
end

function Sounds.playCatch()
	local s = makeSound("rbxassetid://9114251010", 0.5, 1.2)
	s:Play()
end

function Sounds.playCoin()
	local s = makeSound("rbxassetid://131961136", 0.6, 1.5)
	s:Play()
end

function Sounds.playWaveAlarm()
	local s = makeSound("rbxassetid://9114223173", 0.8, 1.0)
	s:Play()
end

function Sounds.playRebirth()
	local s = makeSound("rbxassetid://9114223173", 0.9, 1.8)
	s:Play()
end

function Sounds.playSteal()
	local s = makeSound("rbxassetid://9114251010", 0.7, 0.6)
	s:Play()
end

return Sounds
