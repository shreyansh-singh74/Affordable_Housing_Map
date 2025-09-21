const Footer = () => {
  return (
    <footer className="py-12 bg-surface border-t border-border">
      <div className="container mx-auto px-container">
        <div className="text-center">
          <h3 className="text-2xl font-bold font-heading text-foreground mb-8">
            Affordable Housing Needs Mapper
          </h3>
          
          <div className="flex flex-col sm:flex-row justify-center items-center gap-8 mb-8">
            <a 
              href="#about" 
              className="text-muted-foreground hover:text-primary transition-colors duration-200"
            >
              About
            </a>
            <a 
              href="#contact" 
              className="text-muted-foreground hover:text-primary transition-colors duration-200"
            >
              Contact
            </a>
            <a 
              href="#privacy" 
              className="text-muted-foreground hover:text-primary transition-colors duration-200"
            >
              Privacy
            </a>
          </div>
          
          <div className="text-sm text-muted-foreground">
            © 2024 Affordable Housing Needs Mapper. Building stronger communities through data.
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;