
		local oldInterfaceModeHandler = OldInterfaceModeChangeHandler[oldInterfaceMode];
		if oldInterfaceModeHandler then
			oldInterfaceModeHandler();
		end
		
		-- update the cursor to reflect this mode - these cursor are defined in Civ5CursorInfo.xml
		local cursorIndex = GameInfoTypes[GameInfo.InterfaceModes[newInterfaceMode].CursorType];
		if cursorIndex then
			UIManager:SetUICursor(cursorIndex);
		else
			UIManager:SetUICursor(defaultCursor);
		end
		
		-- do any setup for the new mode
		local newInterfaceModeHandler = NewInterfaceModeChangeHandler[newInterfaceMode];
		if newInterfaceModeHandler then
			newInterfaceModeHandler();
		end
	end
end
Events.InterfaceModeChanged.Add( OnInterfaceModeChanged );


----------------------------------------------------------------        
----------------------------------------------------------------        
function OnActivePlayerTurnEnd()
	UIManager:SetUICursor(1); -- busy
end
Events.ActivePlayerTurnEnd.Add( OnActivePlayerTurnEnd );

function OnActivePlayerTurnStart()
	local interfaceMode = UI.GetInterfaceMode();
	local cursorIndex = GameInfoTypes[GameInfo.InterfaceModes[interfaceMode].CursorType];
	if cursorIndex then
		UIManager:SetUICursor(cursorIndex);
	else
		UIManager:SetUICursor(defaultCursor);
	end
end
Events.ActivePlayerTurnStart.Add( OnActivePlayerTurnStart );

----------------------------------------------------------------
-- 'Active' (local human) player has changed
----------------------------------------------------------------
function OnActivePlayerChanged(iActivePlayer, iPrevActivePlayer)

	-- Reset the alert