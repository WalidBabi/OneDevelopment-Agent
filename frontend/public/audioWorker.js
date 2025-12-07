/**
 * Web Worker for Audio Processing
 * Offloads audio processing to background thread for better UI responsiveness
 */

// Listen for messages from main thread
self.onmessage = function(e) {
  const { type, data } = e.data;
  
  switch (type) {
    case 'processAudio':
      processAudio(data);
      break;
    case 'convertToPCM':
      convertToPCM(data);
      break;
    default:
      self.postMessage({ type: 'error', message: `Unknown message type: ${type}` });
  }
};

/**
 * Process audio data (decode, resample, convert to PCM)
 */
function processAudio({ audioBase64, targetSampleRate = 24000 }) {
  try {
    // Decode base64 to binary
    const binaryString = atob(audioBase64);
    const audioArray = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      audioArray[i] = binaryString.charCodeAt(i);
    }
    
    // Detect format (WAV has RIFF header)
    const isWAV = audioArray[0] === 0x52 && audioArray[1] === 0x49 && 
                  audioArray[2] === 0x46 && audioArray[3] === 0x46;
    
    if (!isWAV) {
      self.postMessage({ 
        type: 'error', 
        message: 'Only WAV format is supported for processing' 
      });
      return;
    }
    
    // Parse WAV header
    const sampleRate = readUint32(audioArray, 24);
    const numChannels = readUint16(audioArray, 22);
    const bitsPerSample = readUint16(audioArray, 34);
    const dataOffset = findDataChunk(audioArray);
    const dataSize = readUint32(audioArray, dataOffset + 4);
    const audioData = audioArray.slice(dataOffset + 8, dataOffset + 8 + dataSize);
    
    // Convert to PCM
    let pcmData;
    if (bitsPerSample === 16) {
      pcmData = new Int16Array(audioData.buffer, audioData.byteOffset, audioData.length / 2);
    } else if (bitsPerSample === 8) {
      // Convert 8-bit to 16-bit
      pcmData = new Int16Array(audioData.length);
      for (let i = 0; i < audioData.length; i++) {
        pcmData[i] = (audioData[i] - 128) * 256;
      }
    } else {
      self.postMessage({ 
        type: 'error', 
        message: `Unsupported bit depth: ${bitsPerSample}` 
      });
      return;
    }
    
    // Convert to mono if stereo
    let monoData = pcmData;
    if (numChannels === 2) {
      monoData = new Int16Array(pcmData.length / 2);
      for (let i = 0; i < monoData.length; i++) {
        monoData[i] = Math.floor((pcmData[i * 2] + pcmData[i * 2 + 1]) / 2);
      }
    }
    
    // Resample if needed
    let finalData = monoData;
    if (sampleRate !== targetSampleRate) {
      finalData = resample(monoData, sampleRate, targetSampleRate);
    }
    
    // Convert to base64
    const pcmBase64 = arrayBufferToBase64(finalData.buffer);
    
    // Calculate duration
    const duration = finalData.length / targetSampleRate;
    
    self.postMessage({
      type: 'audioProcessed',
      pcmBase64,
      duration,
      sampleRate: targetSampleRate,
      size: finalData.length * 2 // 16-bit = 2 bytes per sample
    });
    
  } catch (error) {
    self.postMessage({ 
      type: 'error', 
      message: `Audio processing error: ${error.message}` 
    });
  }
}

/**
 * Convert audio to PCM format
 */
function convertToPCM({ audioBase64 }) {
  processAudio({ audioBase64, targetSampleRate: 24000 });
}

/**
 * Resample audio using linear interpolation
 */
function resample(input, inputRate, outputRate) {
  const ratio = outputRate / inputRate;
  const outputLength = Math.floor(input.length * ratio);
  const output = new Int16Array(outputLength);
  
  for (let i = 0; i < outputLength; i++) {
    const index = i / ratio;
    const indexFloor = Math.floor(index);
    const indexCeil = Math.min(indexFloor + 1, input.length - 1);
    const fraction = index - indexFloor;
    
    // Linear interpolation
    output[i] = Math.floor(
      input[indexFloor] * (1 - fraction) + input[indexCeil] * fraction
    );
  }
  
  return output;
}

/**
 * Read 16-bit unsigned integer from array
 */
function readUint16(array, offset) {
  return array[offset] | (array[offset + 1] << 8);
}

/**
 * Read 32-bit unsigned integer from array
 */
function readUint32(array, offset) {
  return array[offset] | 
         (array[offset + 1] << 8) | 
         (array[offset + 2] << 16) | 
         (array[offset + 3] << 24);
}

/**
 * Find the 'data' chunk in WAV file
 */
function findDataChunk(array) {
  let offset = 12; // Skip RIFF header
  
  while (offset < array.length - 8) {
    const chunkId = String.fromCharCode(
      array[offset], 
      array[offset + 1], 
      array[offset + 2], 
      array[offset + 3]
    );
    
    if (chunkId === 'data') {
      return offset;
    }
    
    const chunkSize = readUint32(array, offset + 4);
    offset += 8 + chunkSize;
  }
  
  throw new Error('Data chunk not found in WAV file');
}

/**
 * Convert ArrayBuffer to base64
 */
function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}
