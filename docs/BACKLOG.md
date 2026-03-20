# Backlog

## Planned

- [ ] **User-provided reference images** -- When a user says "make it look like this" and provides an image, the agent should pass it as `reference_image_path` to `nano-banana.generate`. The mechanism already exists in the tool but the agent workflow doesn't explicitly handle user-supplied style references. Needs: prompt parsing to detect reference image intent, passing the image path through to generation, and adjusting the style brief to note the reference constraint. Note: must rationalize image upload capability with what Amplifier offers natively -- understand how Amplifier handles user-provided images/files before designing the agent-level flow.
