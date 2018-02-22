from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


#on windows you have to use the docker machine
#you can find it with docker-machine ip
docker_ip = 'http://192.168.99.100:4444/wd/hub'
#docker_ip = 'http://localhost:4444/wd/hub'


chrome = webdriver.Remote(
          command_executor=docker_ip,
          desired_capabilities=DesiredCapabilities.CHROME)
firefox = webdriver.Remote(
          command_executor=docker_ip,
          desired_capabilities=DesiredCapabilities.FIREFOX)

chrome.get('https://campus.msm.nl')
print(chrome.title)

#%%firefox.get('https://www.google.com')
#%%print(firefox.title)

chrome.quit()
firefox.quit()
