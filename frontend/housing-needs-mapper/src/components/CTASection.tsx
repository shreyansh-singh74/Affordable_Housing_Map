import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const CTASection = () => {
  return (
    <section id="get-started" className="py-section bg-background">
      <div className="container mx-auto px-container text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold font-heading text-foreground mb-8">
            Ready to explore housing needs in your area?
          </h2>
          
          <p className="text-lg text-muted-foreground mb-12 max-w-2xl mx-auto">
            Start mapping affordable housing needs and make data-driven decisions 
            that strengthen your community.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              variant="hero" 
              size="xl"
              className="group shadow-lg hover:shadow-xl"
              onClick={() => window.open('http://localhost:8501', '_blank')}
            >
              Get Started Now
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            
            <Button 
              variant="outline-primary" 
              size="xl"
              className="group"
            >
              Learn More
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTASection;