adk create sample-agent --model gemini-2.5-flash-lite --api_key $GOOGLE_API_KEY
adk create sample-agent --model gemini-2.5-flash-lite --api_key $(python -c "from settings import settings; print(settings.GOOGLE_API_KEY)")
adk web --url_prefix {url_prefix}
adk web sample-agent