@echo off
set JAVA_HOME=C:\Program Files\Java\jdk-21
set AI_MOCK_ENABLED=false
set DEEPSEEK_API_KEY=sk-UBi1VWOQrdUioPO2nmzqXNsfQUkF0diMW5m5oRsQ0tHUqco1
set KIMI_API_KEY=sk-GzJMZZj9bnrXerS48geOuWRi3VO4DGWRVIkTFOKZ6TnCwlLf
set HUNYUAN_API_KEY=sk-C5S5VM1E8UHIQtEvLvUpKPSCJz9T7f7cuZBmRWiq8eWw8KU3
cd /d "e:\CodeBuddy\VeriCart AI\backend"
call "e:\CodeBuddy\VeriCart AI\backend\maven\apache-maven-3.9.9\bin\mvn.cmd" spring-boot:run > "e:\CodeBuddy\VeriCart AI\backend\mvn_run.log" 2>&1
