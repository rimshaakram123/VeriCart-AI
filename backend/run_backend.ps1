$env:JAVA_HOME = 'C:\Program Files\Java\jdk-21'
$env:AI_MOCK_ENABLED = 'false'
$env:DEEPSEEK_API_KEY = 'sk-UBi1VWOQrdUioPO2nmzqXNsfQUkF0diMW5m5oRsQ0tHUqco1'
$env:KIMI_API_KEY = 'sk-GzJMZZj9bnrXerS48geOuWRi3VO4DGWRVIkTFOKZ6TnCwlLf'
$env:HUNYUAN_API_KEY = 'sk-C5S5VM1E8UHIQtEvLvUpKPSCJz9T7f7cuZBmRWiq8eWw8KU3'
Set-Location 'e:\CodeBuddy\VeriCart AI\backend'
& 'e:\CodeBuddy\VeriCart AI\backend\maven\apache-maven-3.9.9\bin\mvn.cmd' spring-boot:run
