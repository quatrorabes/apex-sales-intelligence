import React, { useState } from 'react';
import { X, Check, ArrowRight, Rocket } from 'lucide-react';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OnboardingModal: React.FC<OnboardingModalProps> = ({ isOpen, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: 'Welcome to Apex Intelligence',
      description: 'Your AI-powered sales intelligence platform that helps you prioritize and engage with the right contacts at the right time.',
      icon: '🎯',
    },
    {
      title: "Today's Board",
      description: 'Get personalized daily recommendations for which contacts to reach out to, based on relationship health, opportunity signals, and engagement patterns.',
      icon: '📊',
    },
    {
      title: 'AI-Powered Scoring',
      description: 'Every contact is automatically scored using our MDCP (conversion likelihood), Priority (urgency), and RSS (relationship strength) algorithms.',
      icon: '🤖',
    },
    {
      title: 'Content Generation',
      description: 'Generate personalized emails, LinkedIn messages, and call scripts tailored to each contact using AI that understands your relationships.',
      icon: '✨',
    },
    {
      title: 'Ready to Start',
      description: "You're all set! Import your contacts from HubSpot or start adding them manually to unlock the full power of Apex Intelligence.",
      icon: '🚀',
    },
  ];

  if (!isOpen) return null;

  const currentStepData = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;

  const handleNext = () => {
    if (isLastStep) {
      onClose();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Getting Started</h2>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded-lg transition"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="flex gap-2">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`h-1 flex-1 rounded-full transition ${
                  index <= currentStep ? 'bg-white' : 'bg-white/30'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-8">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">{currentStepData.icon}</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              {currentStepData.title}
            </h3>
            <p className="text-gray-600 text-lg leading-relaxed">
              {currentStepData.description}
            </p>
          </div>

          {/* Step Counter */}
          <div className="text-center text-sm text-gray-500 mb-6">
            Step {currentStep + 1} of {steps.length}
          </div>

          {/* Navigation */}
          <div className="flex gap-3">
            {currentStep > 0 && (
              <button
                onClick={() => setCurrentStep(currentStep - 1)}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
              >
                Previous
              </button>
            )}
            <button
              onClick={handleNext}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-medium"
            >
              {isLastStep ? (
                <>
                  <Rocket className="h-5 w-5" />
                  Get Started
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
