from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from utils.logger import logger


class RobotsChecker:
    
    def __init__(self):
        self.parsers = {}
    
    def can_fetch(self, url, user_agent="BrochureBot/1.0"):
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        if base_url not in self.parsers:
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
                self.parsers[base_url] = parser
                logger.info(f"robots.txt leido de {base_url}")
            except Exception as e:
                logger.warning(f"No se pudo leer robots.txt de {base_url}: {e}")
                self.parsers[base_url] = None
        
        parser = self.parsers[base_url]
        
        if parser is None:
            return True
        
        allowed = parser.can_fetch(user_agent, url)
        
        if not allowed:
            logger.warning(f"URL bloqueada por robots.txt: {url}")
        
        return allowed


robots_checker = RobotsChecker()