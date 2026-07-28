# AI Scalper Pro [1Min] - TradingView Premium Indicator

## ગુજરાતી માર્ગદર્શિકા (Gujarati Guide)

આ સૂચક (Indicator) ખાસ કરીને **1 મિનિટ (1m)** ચાર્ટ પર ટૂંકા ગાળાના (Scalping) ટ્રેડિંગ માટે મશીન લર્નિંગ અને AI કન્સેપ્ટ્સ સાથે તૈયાર કરવામાં આવ્યો છે. તે અનેક ટેકનિકલ ફિલ્ટર્સ અને માર્કેટ સ્ટ્રક્ચરને જોડીને અત્યંત સચોટ **BUY** અને **SELL** સિગ્નલ આપે છે.

### મુખ્ય સુવિધાઓ (Key Features):
1. **AI કોન્ફિડન્સ સ્કોર (AI Confidence Score - 0 થી 100%)**: અલગ અલગ 7 પરિબળોના આધારે કોન્ફિડન્સ સ્કોર નક્કી થાય છે. (જેમ કે ટ્રેન્ડ, વોલ્યુમ, કેન્ડલસ્ટિક પેટર્ન વગેરે).
2. **Kaufman Adaptive Moving Average (KAMA)**: માર્કેટની અસ્થિરતા (Volatility) મુજબ આપોઆપ એડજસ્ટ થઈને સાચો ટ્રેન્ડ બતાવે છે.
3. **Hurst Exponent**: બજાર ટ્રેન્ડિંગ છે કે ચોપી (sideways) તે નક્કી કરે છે, જેથી ખોટા ટ્રેડથી બચી શકાય.
4. **Linear Regression Forecast**: આગામી 2 કેન્ડલ માટે ભાવની સંભવિત દિશા પ્રિડિક્ટ કરે છે.
5. **કેન્ડલસ્ટિક પેટર્ન AI (Candlestick Pattern AI)**: Bullish Engulfing, Bearish Engulfing, Hammer, Shooting Star, Morning/Evening Star જેવી પેટર્ન આપોઆપ સ્કેન કરે છે.
6. **Dynamic SL/TP (ATR-based)**: ટ્રેડ લીધા પછી આપોઆપ સ્ટોપ લોસ અને ટાર્ગેટ લાઈન્સ સ્ક્રીન પર ડ્રો થાય છે.
7. **લાઈવ ડેશબોર્ડ (Live HUD Table)**: ચાર્ટની જમણી બાજુ લાઈવ વિન રેટ (Win Rate), કોન્ફિડન્સ લેવલ, અને માર્કેટ કન્ડિશન પ્રદર્શિત થાય છે.

### સેટઅપ અને ઇન્સ્ટોલેશન (Setup & Installation):
1. **ચાર્ટ સેટઅપ**: TradingView ઓપન કરો અને કોઈ પણ જોડી (દા.ત. BTCUSD, EURUSD, NIFTY) નો **1 મિનિટ (1m)** ચાર્ટ ઓપન કરો.
2. **પાઈન એડિટર (Pine Editor)**: નીચે આપેલા "Pine Editor" ટેબ પર ક્લિક કરો.
3. **કોડ પેસ્ટ**: `AI_Scalper_Pro_1Min.pine` ફાઈલનો સંપૂર્ણ કોડ કોપી કરી ત્યાં પેસ્ટ કરો.
4. **સેવ કરો**: "Save" કરી "Add to Chart" બટન પર ક્લિક કરો.
5. **અલર્ટ્સ સેટ કરો (Alerts)**: ઇન્ડિકેટર પર રાઈટ ક્લિક કરી "Add Alert" સિલેક્ટ કરો અને **AI BUY ALERT** અથવા **AI SELL ALERT** સેટ કરો.

---

## English Guide

**AI Scalper Pro [1Min]** is a premium, lightweight, and powerful TradingView Pine Script v5 indicator custom-engineered for **1-minute (1m) scalping**. It uses artificial intelligence-inspired multi-factor confluence scoring to deliver noise-free, high-probability BUY and SELL trading signals without lagging or causing script execution timeouts.

### Advanced Features:
- **Kaufman Adaptive Moving Average (KAMA)**: Dynamically adjusts to market efficiency and noise to identify high-quality trend regimes.
- **Hurst Exponent Market Regime Classifier**: Calculates the fractal dimension to distinguish between trending and choppy (mean-reverting) states, effectively filtering out noisy sideways ranges.
- **Linear Regression Forecast**: Employs mathematical linear regression curves to project the future 2-bar path of prices.
- **Candlestick Pattern AI Engine**: Automatically identifies top-tier reversal formations (Engulfing, Hammers, Shooting Stars, Morning & Evening Stars).
- **Multi-Technical Confirmation Index (RSI, MACD, Volume Spikes, VWAP)**: Cross-verifies momentum and high-volume institutional activity before issuing triggers.
- **Dynamic ATR-based Take Profit (TP) & Stop Loss (SL)**: Plots dynamic target and exit boundaries calculated directly from True Range volatility.
- **Live Interactive HUD**: Displays current win rate, total trades, confidence metrics, and momentum states in real-time.

### Optimizing for 1-Minute (1m) Charts:
- **Min Confidence %**: Default `65.0%`. For strict entry, increase to `75%` or higher.
- **Min Confirmations**: Default `3`. Requires at least 3 indicators to agree.
- **Cooldown**: Default `5` bars. Prevents trade spamming during volatile ranges.
