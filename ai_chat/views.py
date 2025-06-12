import json
import os
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

# The system prompt for the AI assistant
SYSTEM_PROMPT = """你是一名优秀的眼科疾病诊断医生，可以对各种眼科疾病给出详细描述，建议以及医疗方案。
请以专业、严谨、易懂的方式回答用户的问题。如果用户询问的问题超出了眼科范围，请礼貌地告知用户你只能回答眼科相关的问题。
回答要有条理，适当使用分点叙述，易于阅读。"""

@csrf_exempt
@require_POST
def ai_chat(request):
    """API endpoint for AI chat using DeepSeek API"""
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': '消息不能为空'}, status=400)
        
        # Get API key from environment variable or settings
        api_key = "sk-83dfd6dc3e9f4ddaa71941fc76ff3941"
        
        if not api_key:
            # For demo purposes, provide a placeholder response when no API key is available
            return JsonResponse({'response': '这是一个演示回复。在实际部署中，您需要配置DeepSeek API密钥才能获取真实的AI回复。请在settings.py中设置DEEPSEEK_API_KEY或添加环境变量。'}, status=200)
        
        # DeepSeek API endpoint
        url = "https://api.deepseek.com/v1/chat/completions"
        
        # Prepare the headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Prepare the payload
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Make the API request with increased timeout and retry logic
        max_retries = 2
        current_retry = 0
        success = False
        
        while current_retry <= max_retries and not success:
            try:
                # Increase timeout to 60 seconds
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                response_data = response.json()
                success = True
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                current_retry += 1
                if current_retry > max_retries:
                    # If all retries failed, return a fallback response
                    return JsonResponse({
                        'response': '抱歉，AI服务暂时无法连接。请尝试以下操作：\n\n1. 稍后再试\n2. 检查您的网络连接\n3. 如果问题持续存在，请联系系统管理员'
                    })
                # Wait before retrying (exponential backoff)
                import time
                time.sleep(1 * current_retry)
        
        # Check if the response contains the expected data
        if 'choices' in response_data and len(response_data['choices']) > 0:
            assistant_response = response_data['choices'][0]['message']['content']
            return JsonResponse({'response': assistant_response})
        else:
            return JsonResponse({'error': '无效的API响应'}, status=500)
            
    except Exception as e:
        # Log the error (in a real app, you'd use proper logging)
        print(f"Error in AI chat: {str(e)}")
        return JsonResponse({'error': f'处理请求时出错: {str(e)}'}, status=500)
