#!/usr/bin/env python3
"""
LinkedIn Daily Automation Script
Generates LinkedIn posts using Claude + Creates images with DALL-E + Posts via LinkedIn API
"""

import os
import json
import sys
from datetime import datetime, timedelta
import anthropic
import requests
from typing import Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Load configuration from environment variables"""
    
    # Claude API
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    
    # LinkedIn API
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    LINKEDIN_PERSON_ID = os.getenv("LINKEDIN_PERSON_ID", "")
    
    # OpenAI (DALL-E for images)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Automation Settings
    ENABLE_IMAGE_GENERATION = os.getenv("ENABLE_IMAGE_GENERATION", "true").lower() == "true"
    ENABLE_LINKEDIN_POSTING = os.getenv("ENABLE_LINKEDIN_POSTING", "false").lower() == "true"
    TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
    
    # Content Settings
    DOMAIN_NAME = os.getenv("DOMAIN_NAME", "My Web Domain")
    DOMAIN_NICHE = os.getenv("DOMAIN_NICHE", "web design")
    
    # Logging
    LOG_FILE = "linkedin_automation.log"
    OUTPUT_DIR = "linkedin_posts"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY environment variable not set")
        if cls.ENABLE_LINKEDIN_POSTING and not cls.LINKEDIN_ACCESS_TOKEN:
            raise ValueError("LINKEDIN_ACCESS_TOKEN required for posting")
        print("✅ Configuration validated")


# ============================================================================
# LOGGING
# ============================================================================

class Logger:
    """Simple logging to file and console"""
    
    def __init__(self, filename):
        self.filename = filename
        self.ensure_dir()
    
    def ensure_dir(self):
        """Ensure output directory exists"""
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(log_entry)
        
        with open(self.filename, "a") as f:
            f.write(log_entry + "\n")
    
    def error(self, message: str):
        self.log(message, "ERROR")
    
    def success(self, message: str):
        self.log(message, "SUCCESS")
    
    def info(self, message: str):
        self.log(message, "INFO")

logger = Logger(Config.LOG_FILE)


# ============================================================================
# CLAUDE API - POST GENERATION
# ============================================================================

class PostGenerator:
    """Generate LinkedIn posts using Claude"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model = "claude-opus-4-1"
        self.max_tokens = 1500
        self.topics = [
            "why your domain extension matters for credibility",
            "common domain management mistakes that cost money",
            "how to audit your domain portfolio for vulnerabilities",
            "domain strategy for personal brands vs companies",
            "the future of domain extensions in 2025",
            "why cheap domains lead to expensive problems",
            "domain security: what most people get wrong",
            "how to build brand recognition through your domain",
            "domain SEO: myths vs reality",
            "why your domain renewal process needs automation"
        ]
    
    def generate_post(self, topic: Optional[str] = None) -> dict:
        """
        Generate a LinkedIn post using Claude with the automation skill
        
        Returns:
            dict: {"post_copy", "image_prompt", "posting_time", "engagement_hook"}
        """
        
        if not topic:
            import random
            topic = random.choice(self.topics)
        
        logger.info(f"Generating post for topic: {topic}")
        
        prompt = f"""You are a LinkedIn content expert. Generate a LinkedIn post about: "{topic}"

Focus on: {Config.DOMAIN_NICHE}
Domain/Brand: {Config.DOMAIN_NAME}

Follow the Claude Skill "LinkedIn Post Generator for Domain Marketing":
- Use the exact output format specified
- Generate educational, opinionated, or behind-the-scenes content
- Include an image prompt for DALL-E
- Suggest optimal posting time
- Include engagement hooks

Output ONLY in this exact format:
🎯 POST COPY:
[post text]

📸 IMAGE PROMPT:
[prompt for DALL-E]

⏰ SUGGESTED POSTING TIME:
[Day, HH:MM format]

💡 ENGAGEMENT HOOK:
[what sparks engagement]"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            parsed = self._parse_response(response_text)
            
            logger.success(f"Post generated successfully")
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to generate post: {str(e)}")
            raise
    
    def _parse_response(self, response: str) -> dict:
        """Parse Claude's formatted response"""
        
        result = {
            "post_copy": "",
            "image_prompt": "",
            "posting_time": "",
            "engagement_hook": ""
        }
        
        # Split by sections
        if "🎯 POST COPY:" in response:
            post_section = response.split("🎯 POST COPY:")[1].split("📸 IMAGE PROMPT:")[0].strip()
            result["post_copy"] = post_section
        
        if "📸 IMAGE PROMPT:" in response:
            image_section = response.split("📸 IMAGE PROMPT:")[1].split("⏰ SUGGESTED POSTING TIME:")[0].strip()
            result["image_prompt"] = image_section
        
        if "⏰ SUGGESTED POSTING TIME:" in response:
            time_section = response.split("⏰ SUGGESTED POSTING TIME:")[1].split("💡 ENGAGEMENT HOOK:")[0].strip()
            result["posting_time"] = time_section
        
        if "💡 ENGAGEMENT HOOK:" in response:
            hook_section = response.split("💡 ENGAGEMENT HOOK:")[1].strip()
            result["engagement_hook"] = hook_section
        
        return result


# ============================================================================
# IMAGE GENERATION - DALL-E
# ============================================================================

class ImageGenerator:
    """Generate images using DALL-E API"""
    
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.endpoint = "https://api.openai.com/v1/images/generations"
    
    def generate_image(self, prompt: str, filename: str) -> Optional[str]:
        """
        Generate image from prompt using DALL-E
        
        Args:
            prompt: Image description
            filename: Where to save the image
        
        Returns:
            Path to saved image or None
        """
        
        if not self.api_key:
            logger.info("OPENAI_API_KEY not set, skipping image generation")
            return None
        
        logger.info(f"Generating image with DALL-E...")
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "standard"
            }
            
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            
            image_url = response.json()["data"][0]["url"]
            
            # Download and save image
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            filepath = os.path.join(Config.OUTPUT_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(img_response.content)
            
            logger.success(f"Image saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return None


# ============================================================================
# LINKEDIN API - POSTING
# ============================================================================

class LinkedInPoster:
    """Post content to LinkedIn using official API"""
    
    def __init__(self):
        self.access_token = Config.LINKEDIN_ACCESS_TOKEN
        self.person_id = Config.LINKEDIN_PERSON_ID
        self.endpoint = "https://api.linkedin.com/rest/posts"
    
    def post_to_linkedin(self, post_text: str, image_path: Optional[str] = None) -> bool:
        """
        Post to LinkedIn
        
        Args:
            post_text: The post content
            image_path: Optional path to image file
        
        Returns:
            bool: Success or failure
        """
        
        if not Config.ENABLE_LINKEDIN_POSTING:
            logger.info("LinkedIn posting disabled (TEST_MODE). Skipping actual post.")
            return True
        
        logger.info("Posting to LinkedIn...")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "LinkedIn-Version": "202401"
            }
            
            payload = {
                "author": f"urn:li:person:{self.person_id}",
                "commentary": post_text,
                "visibility": "PUBLIC"
            }
            
            # If image provided, add it
            if image_path and os.path.exists(image_path):
                payload["content"] = {
                    "media": {
                        "title": "Post Image",
                        "id": self._upload_image(image_path)
                    }
                }
            
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            post_urn = response.json().get("id", "unknown")
            logger.success(f"Posted to LinkedIn: {post_urn}")
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn posting failed: {str(e)}")
            return False
    
    def _upload_image(self, filepath: str) -> str:
        """Upload image to LinkedIn media service"""
        # Simplified - in production you'd use LinkedIn's asset upload endpoint
        logger.info(f"Image attached: {filepath}")
        return "image-id-placeholder"


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

class LinkedInAutomation:
    """Main automation orchestrator"""
    
    def __init__(self):
        Config.validate()
        self.post_generator = PostGenerator()
        self.image_generator = ImageGenerator() if Config.ENABLE_IMAGE_GENERATION else None
        self.linkedin_poster = LinkedInPoster()
    
    def run_daily(self):
        """Run the daily automation cycle"""
        
        logger.info("=" * 60)
        logger.info("LinkedIn Automation Daily Run Started")
        logger.info("=" * 60)
        
        try:
            # Step 1: Generate post
            logger.info("Step 1/3: Generating post...")
            post_data = self.post_generator.generate_post()
            
            # Step 2: Generate image
            image_path = None
            if self.image_generator:
                logger.info("Step 2/3: Generating image...")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = self.image_generator.generate_image(
                    post_data["image_prompt"],
                    f"linkedin_post_{timestamp}.png"
                )
            else:
                logger.info("Step 2/3: Image generation disabled")
            
            # Step 3: Post to LinkedIn
            logger.info("Step 3/3: Posting to LinkedIn...")
            success = self.linkedin_poster.post_to_linkedin(
                post_data["post_copy"],
                image_path
            )
            
            # Save post data for record
            self._save_post_record(post_data, image_path, success)
            
            if success:
                logger.success("Automation cycle completed successfully!")
            else:
                logger.error("Automation cycle completed with errors")
            
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Automation failed: {str(e)}")
            raise
    
    def _save_post_record(self, post_data: dict, image_path: Optional[str], success: bool):
        """Save post record to JSON for tracking"""
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "post_copy": post_data["post_copy"],
            "image_prompt": post_data["image_prompt"],
            "image_path": image_path,
            "posting_time": post_data["posting_time"],
            "engagement_hook": post_data["engagement_hook"]
        }
        
        filename = os.path.join(
            Config.OUTPUT_DIR,
            f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(filename, "w") as f:
            json.dump(record, f, indent=2)
        
        logger.info(f"Post record saved: {filename}")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    
    automation = LinkedInAutomation()
    automation.run_daily()


if __name__ == "__main__":
    main()
