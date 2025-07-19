import cv2
import face_recognition
import numpy as np
import os
import sys
import threading
import queue
import time # For potential sleep in reader thread

# --- FrameReader Class for Multi-threaded Video Capture ---
class FrameReader:
    """
    A class to read video frames in a separate thread, buffering them in a queue.
    This prevents the main processing thread from being blocked by I/O operations.
    """
    def __init__(self, video_path, queue_max_size=128):
        self.video_path = video_path
        self.cap = None
        self.q = queue.Queue(maxsize=queue_max_size)
        self.stopped = False
        self.thread = threading.Thread(target=self._reader_loop, args=())
        self.thread.daemon = True # Allow the program to exit even if this thread is still running

    def start(self):
        """Starts the frame reading thread."""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print(f"Error: Could not open video file '{self.video_path}' in FrameReader.")
            self.stopped = True
            return None # Indicate failure to start
        self.thread.start()
        return self

    def _reader_loop(self):
        """The main loop for the reading thread. Reads frames and puts them into the queue."""
        while not self.stopped:
            if not self.q.full():
                ret, frame = self.cap.read()
                if not ret:
                    # End of video or error reading frame
                    self.stopped = True
                    break
                self.q.put(frame)
            else:
                # Queue is full, pause briefly to avoid busy-waiting and let consumer catch up
                time.sleep(0.001) # Small sleep to yield control

    def read(self):
        """Retrieves the next frame from the queue."""
        if self.q.empty() and self.stopped:
            # If the reader has stopped and the queue is empty, no more frames will come
            return None
        try:
            return self.q.get(timeout=1) # Wait up to 1 second for a frame
        except queue.Empty:
            return None # No frame available within timeout

    def running(self):
        """Checks if the reader thread is still active or if there are frames left in the queue."""
        return not self.stopped or not self.q.empty()

    def stop(self):
        """Stops the frame reading thread and releases video resources."""
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join() # Wait for the thread to finish its current task
        if self.cap:
            self.cap.release()
        print("FrameReader stopped and resources released.")


def extract_character_clips(video_path, character_image_path, output_dir="output_clips", tolerance=0.6, frames_after_detection=30, scale_factor=0.5):
    """
    Searches a video for a specific character and extracts clips where the character is present.
    This version only generates timestamps, it does NOT save video clips.

    Args:
        video_path (str): Path to the input video file.
        character_image_path (str): Path to an image of the character to search for.
        output_dir (str): Directory (not used for saving clips in this version).
        tolerance (float): How much distance between faces to consider a match. Lower is stricter.
                           (0.6 is a common default for face_recognition)
        frames_after_detection (int): Number of frames to continue considering character present
                                      after the last detection, to define clip end.
        scale_factor (float): Factor by which to scale down frames for faster face detection.
                              e.g., 0.5 means 50% of original size. Set to 1.0 for no scaling.
    """

    # --- Fix 1: Check Python Version (informational, not a hard stop) ---
    if sys.version_info >= (3, 13):
        print("WARNING: You are using Python 3.13 or newer. face_recognition (and its underlying dlib library)")
        print("might not have full, stable support for this version yet. If you encounter issues,")
        print("consider trying Python 3.10, 3.11, or 3.12 in a virtual environment.")
        print("-" * 60)

    # No need to create output_dir if not saving clips
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    # 1. Load character image and encode face
    try:
        character_image = face_recognition.load_image_file(character_image_path)
        character_face_encodings = face_recognition.face_encodings(character_image)

        if not character_face_encodings:
            print(f"Error: No face found in the character image '{character_image_path}'. "
                  "Please provide a clear image of the character's face.")
            return []

        known_character_encoding = character_face_encodings[0]
        print(f"Character '{os.path.basename(character_image_path)}' encoding loaded successfully.")

    except FileNotFoundError:
        print(f"Error: Character image not found at '{character_image_path}'.")
        return []
    except Exception as e:
        print(f"Error loading or encoding character image: {e}")
        return []

    # 2. Initialize and start FrameReader (reading thread)
    frame_reader = FrameReader(video_path)
    if not frame_reader.start(): # Check if FrameReader started successfully
        return []

    # Get video properties from the FrameReader's internal capture object
    # (assuming it started successfully and cap is available)
    fps = int(frame_reader.cap.get(cv2.CAP_PROP_FPS))
    width = int(frame_reader.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(frame_reader.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Not needed if not writing clips

    # output_clip_counter = 0 # Not strictly needed if not naming clips
    # out = None # Not needed if not writing clips
    recording_active = False
    frames_since_last_detection = 0

    clip_timestamps = [] # List to store (start_time, end_time) of clips
    current_clip_start_frame = -1

    print("Starting multi-threaded video processing for timestamp extraction...")
    print(f"Video resolution: {width}x{height}, FPS: {fps}")
    print(f"Processing frames at scale factor: {scale_factor}")


    frame_count = 0
    # Main processing loop (acts as the processing thread)
    while frame_reader.running():
        frame = frame_reader.read()
        if frame is None:
            # No more frames from the reader, and reader has stopped
            break

        frame_count += 1
        current_time_seconds = frame_count / fps

        # Resize frame for faster face detection
        if scale_factor != 1.0:
            small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
        else:
            small_frame = frame # No scaling

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)          

        face_locations = face_recognition.face_locations(rgb_small_frame)

        face_encodings = []
        if face_locations:
            try:
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            except Exception as e:
                print(f"Error getting face encodings for frame {frame_count}: {e}")
                print(f"Debug Info: frame shape={rgb_small_frame.shape}, face_locations={face_locations}")
                face_encodings = []

        character_found_in_frame = False
        for i, face_encoding in enumerate(face_encodings):
            matches = face_recognition.compare_faces([known_character_encoding], face_encoding, tolerance=tolerance)
            
            if True in matches:
                character_found_in_frame = True
                frames_since_last_detection = 0
                break

        if character_found_in_frame:
            if not recording_active:
                # Started a new detection period
                recording_active = True
                current_clip_start_frame = frame_count
                print(f"Character detected. Starting new timestamp period at time {current_time_seconds:.2f}s")
            # No 'out.write(frame)' needed here
        else:
            if recording_active:
                frames_since_last_detection += 1
                if frames_since_last_detection > frames_after_detection:
                    # Stop recording the current clip
                    recording_active = False
                    
                    clip_end_frame = frame_count - 1 # The frame before we stopped (or the last frame where character was considered present)
                    clip_end_time = clip_end_frame / fps
                    if current_clip_start_frame != -1:
                        clip_start_time = current_clip_start_frame / fps
                        clip_timestamps.append((clip_start_time, clip_end_time))
                    
                    # output_clip_counter += 1 # Not needed if not naming clips
                    frames_since_last_detection = 0
                    print(f"Character not detected for {frames_after_detection} frames. Ending current timestamp period. Duration: {clip_end_time - clip_start_time:.2f}s")
                    current_clip_start_frame = -1
            
        if frame_count % (fps * 10) == 0:
            print(f"Processed {frame_count} frames...")


    # Finalize any active timestamp period at the end of the video
    if recording_active and current_clip_start_frame != -1:
        clip_end_frame = frame_count # Last frame of the video
        clip_end_time = clip_end_frame / fps
        clip_start_time = current_clip_start_frame / fps
        clip_timestamps.append((clip_start_time, clip_end_time))

    frame_reader.stop() # Ensure the reader thread is properly stopped
    cv2.destroyAllWindows() # Ensures any OpenCV windows are closed
    print("Video processing for timestamps complete.")
    
    # final_clips_count = output_clip_counter + (1 if recording_active else 0) # Not relevant if not saving clips
    print(f"Found {len(clip_timestamps)} periods where the character was present.")
    
    return clip_timestamps


if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Create dummy video and character image for testing
    #    (You'd replace these with your actual files)
    
    # Create a dummy character image (replace with a real image of the character)
    dummy_character_image_path = "iron.jpg"
    if not os.path.exists(dummy_character_image_path):
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.circle(dummy_img, (50, 50), 30, (255, 255, 255), -1) # White circle
        cv2.putText(dummy_img, "Char", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
        cv2.imwrite(dummy_character_image_path, dummy_img)
        print(f"Created a dummy character image: {dummy_character_image_path}")
        print("NOTE: For actual face recognition, replace this with a real image of the character's face.")

    # Create a dummy video (replace with your actual video file)
    # For a real test, you'll need a video file. This dummy creation is very basic.
    dummy_video_path = "output2.mp4"
    if not os.path.exists(dummy_video_path):
        print(f"Creating a dummy video file: {dummy_video_path}")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_dummy = cv2.VideoWriter(dummy_video_path, fourcc, 20, (640, 480))
        for i in range(100): # Create 100 frames
            frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            # Simulate character presence in some frames
            if 20 <= i < 50 or 70 <= i < 90:
                cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), -1) # Green square for "character"
            out_dummy.write(frame)
        out_dummy.release()
        print("Dummy video created.")


    input_video = dummy_video_path
    target_character_image = dummy_character_image_path
    output_clips_directory = "chars" # This directory won't be created or used for saving clips in this version

    # Call the function with your paths and optional parameters
    extracted_timestamps = extract_character_clips(
        video_path=input_video,
        character_image_path=target_character_image,
        output_dir=output_clips_directory, # This parameter is now effectively ignored for clip saving
        tolerance=0.6,          # Adjust this if detection is too strict/loose
        frames_after_detection=2 * 20, # 2 seconds * 20 fps = 40 frames (adjust to your video's FPS)
        scale_factor=0.25      # Process frames at half resolution for faster detection
    )
    
    print("\n--- Extracted Character Presence Timestamps ---")
    if extracted_timestamps:
        for i, (start, end) in enumerate(extracted_timestamps):
            print(f"Period {i+1}: Start = {start:.2f}s, End = {end:.2f}s, Duration = {end - start:.2f}s")
    else:
        print("No character presence periods were detected or an error occurred.")

    # You can uncomment these lines to clean up the dummy files after execution
    # if os.path.exists(dummy_video_path):
    #     os.remove(dummy_video_path)
    # if os.path.exists(dummy_character_image_path):
    #     os.remove(dummy_character_image_path)