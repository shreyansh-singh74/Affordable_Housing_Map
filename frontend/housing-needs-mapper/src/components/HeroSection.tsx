import { Button } from "@/components/ui/button";
import heroCityscape from "@/assets/hero-cityscape.jpg";

const HeroSection = () => {
  const scrollToGetStarted = () => {
    const ctaSection = document.getElementById('get-started');
    ctaSection?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${heroCityscape})` }}
      >
        <div className="absolute inset-0 bg-gradient-hero opacity-85"></div>
      </div>
      
      {/* Content */}
      <div className="relative z-10 container mx-auto px-container text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-bold font-heading text-foreground mb-6 leading-tight">
            Mapping Affordable Housing Needs for 
            <span className="text-primary"> Stronger Communities</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
            Using real data to identify where affordable housing is needed most.
          </p>
          
          <Button 
            onClick={() => window.open('http://localhost:8501', '_blank')}
            variant="hero" 
            size="xl"
            className="shadow-hero hover:shadow-lg transform hover:-translate-y-1"
          >
            Get Started
          </Button>
        </div>
      </div>
      
      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-primary rounded-full flex justify-center">
          <div className="w-1 h-3 bg-primary rounded-full mt-2 animate-pulse"></div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;