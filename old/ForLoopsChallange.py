se );
            else
                Controls.ThemPocketDefensivePact:SetHide( true );
                Controls.ThemTableDefensivePact:SetHide( false );
            end
        
        elseif( TradeableItems.TRADE_ITEM_RESEARCH_AGREEMENT == itemType ) then
        
            if( bFromUs ) then
                Controls.UsPocketResearchAgreement:SetHide( true );
                Controls.UsTableResearchAgreement:SetHide( false );
            else
                Controls.ThemPocketResearchAgreement:SetHide( true );
                Controls.ThemTableResearchAgreement:SetHide( false );
            end
        
        elseif( TradeableItems.TRADE_ITEM_TRADE_AGREEMENT == itemType ) then
        
            if( bFromUs ) then
                Controls.UsPocketTradeAgreement:SetHide( true );
                Controls.UsTableTradeAgreement:SetHide( false );
            else
                Controls.ThemPocketTradeAgreement:SetHide( true );
                Controls.ThemTableTradeAgreement:SetHide( false );
            end
        
        elseif( TradeableItems.TRADE_ITEM_RESOURCES 