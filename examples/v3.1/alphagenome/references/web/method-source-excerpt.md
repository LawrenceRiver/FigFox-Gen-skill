MLP
+
+
Pair
Shape (29, 29, 128)
2048 bp resolution
Normalization
Sequence
Pair
Shape (213, 1536)
128 bp resolution
Sequence to 
pair block
+
Shape (29, 29, 128)
2048 bp resolution
Normalization
Row-wise 
attention
Pair update block
× 4
Shape (213, 1536)
128 bp resolution
Pair update
block
Transformer
block
Transformer
block
Transformer
block
Pair update
block
Shape (29, 29, 128)
2048 bp resolution
Transformer tower
Same
resolution
skip connect
Shape (2n–1, c+128)
r bp resolution
Shape (2n, c)
r/2 bp resolution
Shape (2n, c)
r/2 bp resolution
Shape (2n–1, c)
r bp resolution
Conv block
(width=1)
Conv block (width = 5)
Conv block (width = 5)
+
+
+
Repeat × 2
Upres block
Shape (2n, c-128)
r bp resolution
Shape (2n, c)
r bp resolution
Skip connection
shape (2n, c)
2r bp resolution
Shape (2n–1, c)
2r bp resolution
Conv block (width = 5)
Conv block (width = 5)
+
+
Max pool
Downres block
Shape (2n, c)
r bp resolution
Shape (2n, c)
r bp resolution
Conv1D (width = width)
Normalization
GeLU
Conv block (width)
DNA embedder
Input: 1Mb DNA sequence
Downres block 1
Encoder
Decoder
Downres block 6
Upres block 1
Upres block 6
Upres block 7
Output embedder
Transformer
tower
Shape (213, 1536)
128 bp resolution
Shape (220, 4)
1 bp resolution
Shape (219, 768)
2 bp resolution
Shape (218, 896)
4 bp resolution
Shape (219, 896)
2 bp resolution
...
Shape (220, 768)
1 bp resolution
Shape (213, 1536)
128 bp resolution
Shape (214, 1408)
64 bp resolution
Output heads
Shape (218, 1024)
4 bp resolution
...
Shape (214, 1408)
64 bp resolution
2048 bp res pairwise activations
128 bp res activations
b  Detailed diagrams for key model components 
a  AlphaGenome Model Overview 
Outer sum
Linear
Shape (29,  29, 128)
128 bp resolution
+
Positional 
features
Sequence Shape (213, 1536)
128 bp resolution
Pooling
Normalization
Linear
Linear
Linear
Linear
GeLU
q
k
Attention with
pos. encoding
Sequence to pair block
Output embedder
Linear
Linear
Linear
GeLU
Normalization
GeLU
+
Repeat 
128 ×
Shape (213, 1536)
128 bp resolution
Shape (220, 768)
1 bp resolution
Shape (213, 3072)
128 bp resolution
Shape (220, 1536)
1 bp resolution
Normalization
Splice junction head
Positive
strand
Linear
Scale 
and
offset
RoPE
Splice site junctions
Scale 
and
offset
RoPE
Acceptor
Donor
Negative
strand
Scale 
and
offset
RoPE
Scale 
and
offset
RoPE
Donor
Acceptor
Shape (512, 512, 734)
1 bp resolution
Shape (220, 1536)
1 bp resolution
Extended Data Figure 1 | AlphaGenome model architecture. (a) Overview schematic illustrating the flow of activations through the model.
The architecture follows a U-Net-like structure with an Encoder, a central Transformer Tower, and a Decoder processing a 1Mb DNA input
sequence. The Encoder uses convolutional blocks and max pooling to progressively downsample the sequence resolution (from 1 bp to 128 bp)
while increasing feature channels. The Transformer Tower operates at 128 bp resolution, iteratively refining sequence representations and
generating pairwise (2D) representations. The Decoder uses convolutional blocks and upsampling, incorporating skip connections (dashed
lines) from corresponding Encoder stages, to restore sequence resolution up to 1 bp. An Output Embedder performs final processing before
feeding representations to task-specific output heads. (b) Internal structure of key component blocks used repeatedly within the architecture
overview shown in (a). Diagrams detail the layers within the convolutional blocks (Conv block, Upres block), the Transformer blocks, and the
blocks responsible for generating and updating pairwise representations (Pair update block, Sequence to pair block). Tensor shapes are shown
excluding the batch dimension. Abbreviations: r = log-resolution, c = channels.
66
