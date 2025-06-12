from django.conf import settings
from Project.settings import GPT_Key
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

####################
# 2. 辅助函数：生成诊断建议
####################
def generate_diagnosis_advice(patient, record):
    """
    根据患者信息和诊断结果生成个性化诊断建议
    
    Args:
        patient: Patient模型实例，包含患者基本信息
        record: Record模型实例，包含诊断结果
        
    Returns:
        str: 生成的诊断建议文本
    """
    # 记录函数调用信息
    logger.info(f"生成诊断建议 - 患者ID: {patient.id}, 记录ID: {record.id}")
    
    # 提取患者信息
    age = patient.age
    gender = "男" if patient.gender == "Male" else "女"
    diagnosis_result = record.result if record.result else "待诊断"
    
    logger.info(f"患者信息 - 年龄: {age}, 性别: {gender}, 诊断结果: {diagnosis_result}")
    
    # 基于诊断结果生成建议
    if diagnosis_result == "待诊断":
        from .inference import analyze_image
        
        # 如果结果是待诊断，调用模型进行诊断
        if record.processed_image:
            try:
                import os
                from django.conf import settings
                
                # 确保图像路径正确
                image_path = os.path.join(settings.MEDIA_ROOT, str(record.processed_image))
                logger.info(f"分析图像 - 路径: {image_path}")
                
                analysis_result = analyze_image(image_path)
                logger.info(f"分析结果: {analysis_result}")
                
                if isinstance(analysis_result, dict) and 'diagnosis' in analysis_result:
                    diagnosis_result = analysis_result['diagnosis']
                    confidence = analysis_result.get('confidence', 0)
                    
                    # 更新记录
                    record.result = diagnosis_result
                    record.save()
                    
                    logger.info(f"更新诊断结果: {diagnosis_result}")
                else:
                    return "诊断失败，请重新上传图像或联系技术支持。"
            except Exception as e:
                logger.error(f"诊断过程中出错: {str(e)}")
                return f"诊断过程中出错: {str(e)}"
        else:
            return "无诊断图像，请上传眼底图像后重试。"
    
    # 根据诊断结果和患者信息生成个性化建议
    advice = ""
    
    # 正常情况
    if diagnosis_result == "正常":
        advice = f"尊敬的患者，您的眼底检查结果正常，未发现异常情况。"
        
        if age > 40:
            advice += f"但考虑到您已{age}岁，建议每年进行一次常规眼科检查，保持眼部健康。"
        else:
            advice += f"建议您保持每两年一次的常规眼科检查，并注意用眼卫生。"
        
        advice += "\n\n日常护眼建议：\n"
        advice += "1. 保持良好用眼习惯，每用眼1小时休息10分钟\n"
        advice += "2. 保持均衡饮食，多摄入富含维生素A、C、E的食物\n"
        advice += "3. 避免长时间使用电子设备，注意调整屏幕亮度和使用环境光线\n"
        advice += "4. 保持充足睡眠，减少眼部疲劳"
    
    # 糖尿病视网膜病变
    elif "糖尿病" in diagnosis_result:
        severity = "早期" if 'confidence' in locals() and confidence and confidence < 0.7 else "明显"
        advice = f"您的眼底检查显示有{severity}糖尿病视网膜病变的迹象。"
        
        if age > 60:
            advice += f"考虑到您的年龄为{age}岁，需要更密切地监控病情发展。"
        
        advice += "\n\n建议：\n"
        advice += "1. 严格控制血糖，定期监测血糖水平\n"
        advice += "2. 每3-6个月进行一次眼底检查\n"
        advice += "3. 控制血压和血脂，保持健康生活方式\n"
        advice += "4. 避免剧烈运动和重物提举\n"
        advice += "5. 如有视力变化，请立即就医"
    
    # 青光眼
    elif "青光眼" in diagnosis_result:
        advice = f"您的眼底检查结果提示青光眼相关改变。"
        
        if age > 50:
            advice += f"考虑到您{age}岁的年龄因素，青光眼风险相对较高。"
        
        advice += "\n\n建议：\n"
        advice += "1. 尽快完成全面眼科检查，包括眼压测量、视野检查和前节OCT\n"
        advice += "2. 遵医嘱使用降眼压药物，不要自行停药\n"
        advice += "3. 避免长时间低头或用力活动\n"
        advice += "4. 保持规律作息，避免情绪激动\n"
        advice += "5. 每3个月进行一次眼科随访检查"
    
    # 白内障
    elif "白内障" in diagnosis_result:
        advice = "您的眼底检查结果提示有白内障相关改变。"
        
        if age > 65:
            advice += f"在您{age}岁的年龄，白内障是较为常见的眼部疾病。"
        
        advice += "\n\n建议：\n"
        advice += "1. 完成详细的视力检查和裂隙灯检查评估白内障程度\n"
        advice += "2. 根据视力影响程度考虑手术治疗时机\n"
        advice += "3. 佩戴防紫外线眼镜，减少阳光直射\n"
        advice += "4. 保持健康饮食，多摄入抗氧化物质\n"
        advice += "5. 避免用眼过度疲劳"
    
    # 年龄相关性黄斑变性 (AMD)
    elif "AMD" in diagnosis_result or "黄斑变性" in diagnosis_result:
        advice = "您的眼底检查结果提示有年龄相关性黄斑变性(AMD)的迹象。"
        
        if age > 60:
            advice += f"考虑到您{age}岁的年龄因素，需要密切关注病情变化。"
        
        advice += "\n\n建议：\n"
        advice += "1. 尽快完成OCT和荧光血管造影检查\n"
        advice += "2. 戒烟，并避免二手烟环境\n"
        advice += "3. 增加绿叶蔬菜和富含抗氧化剂的食物摄入\n"
        advice += "4. 定期监测视力变化，注意直线变形等症状\n"
        advice += "5. 根据病情可能需要接受抗VEGF治疗"
    
    # 高血压视网膜病变
    elif "高血压" in diagnosis_result:
        advice = "您的眼底检查结果提示有高血压视网膜病变的迹象。"
        
        if age > 50:
            advice += f"考虑到您{age}岁的年龄，高血压对眼底的损害需要特别关注。"
        
        advice += "\n\n建议：\n"
        advice += "1. 严格控制血压，遵医嘱服用降压药物\n"
        advice += "2. 低盐饮食，控制体重，适量运动\n"
        advice += "3. 每3-6个月进行一次眼底检查\n"
        advice += "4. 避免情绪激动和过度疲劳\n"
        advice += "5. 如有视力变化，请立即就医"
    
    # 近视
    elif "近视" in diagnosis_result:
        advice = "您的眼底检查结果提示有近视相关改变。"
        
        if age < 18:
            advice += f"考虑到您年龄为{age}岁，正处于视力发育阶段，需要特别注意近视的控制。"
        
        advice += "\n\n建议：\n"
        advice += "1. 定期验光，确保佩戴合适度数的眼镜\n"
        advice += "2. 保持正确读写姿势，确保充足光线\n"
        advice += "3. 增加户外活动时间，每天至少2小时\n"
        advice += "4. 使用电子设备时遵循20-20-20法则（每20分钟向20英尺外看20秒）\n"
        advice += "5. 如近视度数快速增长，应考虑近视控制措施"
    
    # 其他疾病/异常
    else:
        advice = f"您的眼底检查结果为：{diagnosis_result}。建议进一步检查以明确诊断。"
        
        advice += "\n\n一般建议：\n"
        advice += "1. 尽快完成全面的眼科检查\n"
        advice += "2. 注意记录视力变化和不适症状\n"
        advice += "3. 避免揉眼和眼部用力\n"
        advice += "4. 保持健康的生活习惯，均衡饮食，充足休息\n"
        advice += "5. 根据后续检查结果调整治疗方案"
    
    # 添加通用结束语
    advice += "\n\n以上建议仅供参考，具体治疗方案请遵医嘱。祝您健康！"
    
    logger.info(f"生成的建议（前50字符）: {advice[:50]}...")
    
    return advice
