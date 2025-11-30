import argparse


class ArgsManager:
    _instance = None
    _args = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ArgsManager, cls).__new__(cls)
        return cls._instance
    
    def parse_args(self):
        parser = argparse.ArgumentParser(description='Generador de Folletos Corporativos con IA')
        
        parser.add_argument('--company', type=str, default='Hugging Face', 
                          help='Nombre de la empresa')
        parser.add_argument('--url', type=str, default='https://huggingface.co', 
                          help='URL del sitio web')
        parser.add_argument('--tone', type=str, choices=['formal', 'humoristico'], 
                          default='formal', help='Tono del folleto')
        parser.add_argument('--language', type=str, default='', help = 'Idioma del folleto')
        parser.add_argument('--format', type=str, nargs='+', 
                    choices=['md', 'html', 'pdf'], 
                    default=['md'], 
                    help='Formatos de salida (md, html, pdf)')
        parser.add_argument('--model', type=str, default='gpt-4o-mini', help='Modelo de OpenAI a utilizar')
        
        self._args = parser.parse_args()
        return self._args
    
    def get(self, arg_name, default=None):
        if self._args is None:
            self.parse_args()
        return getattr(self._args, arg_name, default)
    
    def get_all(self):
        if self._args is None:
            self.parse_args()
        return vars(self._args)


args_manager = ArgsManager()