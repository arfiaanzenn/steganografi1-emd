# app.py

import os
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' # Ganti dengan kunci rahasia yang kuat

# --- Algoritma Edge Mean Difference (EMD) ---

def get_edges(image):
    """Mendeteksi tepi menggunakan operator Sobel."""
    # Konversi gambar ke grayscale
    gray_image = image.convert('L')
    
    # Konversi gambar ke array numpy
    img_array = np.array(gray_image, dtype=np.float32)
    
    # Kernel Sobel
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    
    # Konvolusi
    Gx = np.abs(np.convolve(img_array.flatten(), sobel_x.flatten(), mode='same').reshape(img_array.shape))
    Gy = np.abs(np.convolve(img_array.flatten(), sobel_y.flatten(), mode='same').reshape(img_array.shape))
    
    # Hitung gradien
    gradient = np.sqrt(Gx**2 + Gy**2)
    
    # Terapkan threshold untuk mendapatkan citra biner
    threshold = np.max(gradient) * 0.1 # Contoh threshold
    edges = (gradient > threshold).astype(np.uint8) * 255
    
    return Image.fromarray(edges)

def embed_message(cover_image, message):
    """Menyisipkan pesan ke dalam gambar penutup menggunakan EMD."""
    img = cover_image.convert('RGB')
    width, height = img.size
    pixels = np.array(img)
    
    # Dapatkan citra tepi
    edge_image = get_edges(img)
    edge_pixels = np.array(edge_image)
    
    # Konversi pesan ke biner
    binary_message = ''.join(format(ord(char), '08b') for char in message) + '1111111111111110' # Penanda akhir pesan
    message_length = len(binary_message)
    
    data_index = 0
    for y in range(height):
        for x in range(width):
            # Cek apakah pixel adalah bagian dari tepi
            if edge_pixels[y, x] > 0:
                # Sisipkan 2 bit data ke dalam 1 pixel
                for i in range(3): # R, G, B
                    if data_index < message_length:
                        # Dapatkan nilai bit
                        bit1 = int(binary_message[data_index])
                        bit2 = int(binary_message[data_index + 1]) if data_index + 1 < message_length else 0
                        data_index += 2

                        # Hitung mean difference
                        d = pixels[y, x, i] % 4
                        
                        # Hitung nilai baru
                        new_d = bit1 * 2 + bit2
                        
                        pixels[y, x, i] += new_d - d
                        
                        # Pastikan nilai pixel berada dalam rentang 0-255
                        pixels[y, x, i] = np.clip(pixels[y, x, i], 0, 255)

    return Image.fromarray(pixels.astype('uint8'), 'RGB')

def extract_message(stego_image):
    """Mengekstrak pesan dari gambar stego."""
    img = stego_image.convert('RGB')
    width, height = img.size
    pixels = np.array(img)

    # Dapatkan citra tepi
    edge_image = get_edges(img)
    edge_pixels = np.array(edge_image)
    
    binary_message = ''
    
    for y in range(height):
        for x in range(width):
            # Cek apakah pixel adalah bagian dari tepi
            if edge_pixels[y, x] > 0:
                for i in range(3): # R, G, B
                    # Ekstrak 2 bit dari pixel
                    d = pixels[y, x, i] % 4
                    bit1 = d // 2
                    bit2 = d % 2
                    
                    binary_message += str(bit1) + str(bit2)
                    
                    # Cek penanda akhir pesan
                    if len(binary_message) >= 16 and binary_message[-16:] == '1111111111111110':
                        break
                if len(binary_message) >= 16 and binary_message[-16:] == '1111111111111110':
                    break
        if len(binary_message) >= 16 and binary_message[-16:] == '1111111111111110':
            break

    # Hapus penanda akhir pesan
    binary_message = binary_message[:-16]

    # Konversi biner ke pesan teks
    message = ''
    try:
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i+8]
            message += chr(int(byte, 2))
    except ValueError:
        message = 'Pesan tidak dapat diekstrak atau rusak.'

    return message

# --- Rute Flask ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/steganography', methods=['POST'])
def steganography():
    try:
        # Dapatkan data dari form
        operation = request.form['operation']
        image_file = request.files['image_file']
        
        # Baca gambar dari memori
        image_data = image_file.read()
        image = Image.open(BytesIO(image_data))
        
        if operation == 'embed':
            secret_message = request.form['secret_message']
            if not secret_message:
                return jsonify({'error': 'Pesan rahasia tidak boleh kosong.'}), 400
            
            # Sisipkan pesan
            stego_image = embed_message(image, secret_message)
            
            # Simpan gambar stego ke BytesIO
            img_io = BytesIO()
            stego_image.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Konversi gambar ke base64 untuk ditampilkan di HTML
            encoded_image = base64.b64encode(img_io.read()).decode('utf-8')
            
            return jsonify({
                'success': True, 
                'image': f'data:image/png;base64,{encoded_image}',
                'message': 'Pesan berhasil disisipkan!'
            })
            
        elif operation == 'extract':
            # Ekstrak pesan
            extracted_message = extract_message(image)
            
            return jsonify({
                'success': True,
                'message': 'Pesan berhasil diekstrak!',
                'extracted_message': extracted_message
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)