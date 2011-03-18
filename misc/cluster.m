function [ output_args ] = demo( input_args )
%DEMO Summary of this function goes here
%   Detailed explanation goes here

    n = 100;

    x = randperm(n); 
    gs = 35; 
    group1 = x(1:gs); 
    group2 = x(gs+1:end);
    
    p_group1 = 0.5; 
    p_group2 = 0.4; 
    p_between = 0.1;
    
    
    A(group1, group1) = 0.5*double(rand(gs,gs) < p_group1); 
    A(group2, group2) = 0.4*double(rand(n-gs,n-gs) < p_group2); 
    A(group1, group2) = 0.3*double(rand(gs, n-gs) < p_between); 
    A = triu(A,1);
    A = A + A';
    
    %figure;
    %imagesc(A);

    L = laplacian(A); 
	[V D] = eig(L);

    [V D] = eigs(L, 2, 'SA'); 
    [ignore p] = sort(V(:,2));
	V(p)
    %figure;
    %plot(V(p));
    
    %figure;
    %imagesc(A(p,p));
end


function L = laplacian(A)

    L = diag(sum(A,2)) - A;
    
    %n = size(A,1)
    %L = speye(n) - diag(sum(A,2).^(-1/2)) * A * diag(sum(A,2).^(-1/2));

end
