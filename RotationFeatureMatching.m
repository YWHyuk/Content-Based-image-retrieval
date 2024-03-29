function RotationFeatureMatching(arg1, arg2, arg3, arg4, arg5)
disp(arg1)
disp(arg2)
disp(arg3)
disp(arg4)
disp(arg5)
%% Find Image Rotation and Scale Using Automated Feature Matching
% This example shows how to automatically align two images that differ by a
% rotation and a scale change. It closely parallels another example titled
% <matlab:showdemo('RotationFitgeotransExample') Find Image Rotation and Scale>. 
% Instead of using a manual approach to register the two images, it
% utilizes feature-based techniques found in the Computer Vision System
% Toolbox(TM) to automate the registration process.
%
% In this example, you will use |detectSURFFeatures| and 
% |vision.GeometricTransformEstimator| System object to recover rotation 
% angle and scale factor of a distorted image. You will then transform the 
% distorted image to recover the original image.

% Copyright 1993-2014 The MathWorks, Inc. 

%% Step 1: Read the 1st Image
% Bring an image into the workspace.
% srcFile = 'DJI_0006.JPG';
srcFile = arg1;
whiteFile = arg4;
srcImg  = imread(srcFile);
whiteImg =imread(whiteFile);
% imshow(img1);

%% Step 2: Read the 2nd Image

% tgtFile = 'DJI_0008.JPG';
tgtFile = arg2;

tgtImg  = imread(tgtFile);

% figure, imshow(img2)


%%
% You can experiment by varying the scale and rotation of the input image.
% However, note that there is a limit to the amount you can vary the scale
% before the feature detector fails to find enough features.

%% Step 3: Find Matching Features Between Images
% Detect features in both images.
original  = srcImg(:, :, 1);
distorted = tgtImg(:, :, 1);

ptsOriginal  = detectSURFFeatures(original);
ptsDistorted = detectSURFFeatures(distorted);

%%
% Extract feature descriptors.
[featuresOriginal,   validPtsOriginal]  = extractFeatures(original,  ptsOriginal);
[featuresDistorted, validPtsDistorted]  = extractFeatures(distorted, ptsDistorted);

%%
% Match features by using their descriptors.
indexPairs = matchFeatures(featuresOriginal, featuresDistorted);

%%
% Retrieve locations of corresponding points for each image.
matchedOriginal  = validPtsOriginal(indexPairs(:,1));
matchedDistorted = validPtsDistorted(indexPairs(:,2));

%%
% Show point matches. Notice the presence of outliers.
%figure;
%showMatchedFeatures(original,distorted,matchedOriginal,matchedDistorted);
%title('Putatively matched points (including outliers)');

%% Step 4: Estimate Transformation
% Find a transformation corresponding to the matching point pairs using the
% statistically robust M-estimator SAmple Consensus (MSAC) algorithm, which
% is a variant of the RANSAC algorithm. It removes outliers while computing
% the transformation matrix. You may see varying results of the
% transformation computation because of the random sampling employed by the
% MSAC algorithm.
[tform, inlierDistorted, inlierOriginal] = estimateGeometricTransform(...
    matchedDistorted, matchedOriginal, 'similarity');

%%
% Display matching point pairs used in the computation of the
% transformation matrix.
%figure;
%showMatchedFeatures(original,distorted, inlierOriginal, inlierDistorted);
%title('Matching points (inliers only)');
%legend('ptsOriginal','ptsDistorted');

%% Step 5: Solve for Scale and Angle
% Use the geometric transform, TFORM, to recover 
% the scale and angle. Since we computed the transformation from the
% distorted to the original image, we need to compute its inverse to 
% recover the distortion.
%
%  Let sc = scale*cos(theta)
%  Let ss = scale*sin(theta)
%
%  Then, Tinv = [sc -ss  0;
%                ss  sc  0;
%                tx  ty  1]
%
%  where tx and ty are x and y translations, respectively.
%

%%
% Compute the inverse transformation matrix.
Tinv  = tform.invert.T;

ss = Tinv(2,1);
sc = Tinv(1,1);
scale_recovered = sqrt(ss*ss + sc*sc)
theta_recovered = atan2(ss,sc)*180/pi

%%
% The recovered values should match your scale and angle values selected in
% *Step 2: Resize and Rotate the Image*.

%% Step 6: Recover the Original Image
% Recover the original image by transforming the distorted image.
% outputView = imref2d(size(original));
% recovered  = imwarp(distorted,tform,'OutputView',outputView);
outputView = imref2d(size(srcImg));
recovered  = imwarp(tgtImg,tform,'OutputView',outputView);
white_recovered = imwarp(whiteImg,tform,'OutputView',outputView);
%%
% Compare |recovered| to |original| by looking at them side-by-side in a montage.
imwrite(recovered,arg3);
imwrite(white_recovered,arg5);

%%
% The |recovered| (right) image quality does not match the |original| (left)
% image because of the distortion and recovery process. In particular, the 
% image shrinking causes loss of information. The artifacts around the edges are 
% due to the limited accuracy of the transformation. If you were to detect 
% more points in *Step 4: Find Matching Features Between Images*, 
% the transformation would be more accurate. For example, we could have
% used a corner detector, |detectFASTFeatures|, to complement the SURF 
% feature detector which finds blobs. Image content and image size also 
% impact the number of detected features.



