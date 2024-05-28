%% Set up the Import Options and import the data
opts = delimitedTextImportOptions("NumVariables", 3);

% Specify range and delimiter
opts.DataLines = [200, 8000];
opts.Delimiter = ",";

% Specify column names and types
opts.VariableNames = ["absolute_times", "experiment_times", "e2eLatencyms"];
opts.VariableTypes = ["double", "double", "double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";

path = ['/home/user/Documents/workspace/latency-results/'];

% Get the list of items in the directory
benchmark_dirs = dir(path);

for j = 1:length(benchmark_dirs)
    % Skip '.' and '..' directories
    if strcmp(benchmark_dirs(j).name, '.') || strcmp(benchmark_dirs(j).name, '..')
        continue;
    end

    % Check if the item is a directory
    if benchmark_dirs(j).isdir
        % Print or perform operations on the subdirectory
        disp(['Processing subdirectory: ' benchmark_dirs(j).name]);
        variableName = strcat(strrep(strrep(strrep(strrep(benchmark_dirs(j).name, '-', '_'), 'width', 'w'), 'height', 'h'), 'buffer', 'b'), '_');
     
        files = dir(fullfile(strcat(path,benchmark_dirs(j).name), '*.log'));
        for i=1:length(files)
            % Import the data
            %strcat(variableName, num2str(i))            
            iterationVariable = strcat(variableName, num2str(i));
            data = readtable(strcat(strcat(path, strcat(benchmark_dirs(j).name, '/')), files(i).name), opts);
            eval([iterationVariable ' = data;']);
            disp(['Processing file: ' files(i).name]);
        end
        
    end
end

%% Clear temporary variables
clear opts
