import re

"""Parser for files of StereoGene pipeline and objects for parser"""

class Run:
	"""
	All about the run class
	"""
	def __init__(self, resPath, track1_id, track2_id, prog_run_id, nFgr, nBkg, Fg_Corr, Fg_av_Corr, FgCorr_sd, Bg_Corr, Bg_av_Corr, BgCorr_sd, mann_Z, p_value, date, confounder_id):
		"""
		Basic constructor
		"""
		self.table_id = None
		
		self.track1_id = track1_id
		
		self.track2_id = track2_id
		
		self.prog_run_id = prog_run_id
		
		self.nFgr = nFgr
		
		self.nBkg = nBkg
		
		self.Fg_Corr = Fg_Corr
		
		self.Fg_av_Corr = Fg_av_Corr
	    
		self.FgCorr_sd = FgCorr_sd
        
		self.Bg_Corr = Bg_Corr
	    
		self.Bg_av_Corr = Bg_av_Corr
        
		self.BgCorr_sd = BgCorr_sd
		
		self.mann_z = mann_Z
		
		self.p_value = p_value
		
		self.date = date
		
		
		self.run_file_name = self.getRunFile(track1_id[1], track2_id[1], resPath)
		
		self.confounder_id = confounder_id
		
	def getRunFile(self, track1, track2, path):
		"""
		Form result file name from input file names
		"""
		
		point1 = track1.rfind(".")
		point2 = track2.rfind(".")
		return path + "/" + track1[0:point1] + "~" + track2[0:point2]

	def __str__(self):
		"""
		Form string representation 
		"""
		return "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.table_id, self.track1_id, self.track2_id, self.param_id, self.prog_run_id, self.nFgr, self.Bkg_av, self.Fg_av, self.Bkg_sd, self.Fg_sd, self.tot_cor, self.mann_z, self.p_value, self.P_corr, self.vesion)




class Track:#
	"""
	All about the track class
	"""
	def __init__(self, trackPath, mark, sample, lab, tissue=None, devstage=None, confounder=None):
		"""
		Basic constructor
		"""
		self.table_id = None
		self.trackPath = trackPath
		self.tissue = tissue
		self.mark = mark
		self.sample = sample
		self.lab = lab
		self.devstage = devstage		

	def set_id(self, table_id):
		"""
		Set id for object
		"""
		self.table_id = table_id

class Param:
	"""
	Class to store the parameters of running
	"""
	def __init__(self, paramHash):
		self.paramHash = paramHash
class ConfounderMember:
	"""
	Class to store the confounder member
	"""
	def __init__(self, name, path, eigenValue):
		self.name = name
		self.path = path
		self.eigenValue = eigenValue

class Parser:
	"""
	Parser of results
	"""
	def parseInputFileInfoTable(self, fname):
                """
                Parse info about files table (encode-like),
                For important info_keys see example below,
                the format of line is:
                file_name\tinfo_key1=info_value1; info_key2=info_value2;...info_key3=info_value3
                example:
                UCSF_UBC.Penis_Foreskin_Keratinocyte_Primary_Cells.smRNA_Seq.skin01.wig	project=HEA;  cell=Penis_Foreskin_Keratinocyte_Primary_Cells; antibody=smRNA_Seq; lab=UCSF_UBC; replicate=skin01
                """
                fin = open(fname)
                file_info = {}
                for line in fin:
                        ss = line.split("\t")
                        file_name = ss[0]
                        ind = file_name.rfind(".")
                        file_name = file_name[0:ind]
                        print("=====\n" + file_name)
                        print(ss[1])
                        features = ss[1].split(";")
                        print(features)
                        f_hash = {}
                        for f in features:
                                name, value = f.strip().split("=")
                                f_hash[name] = value

                        print(f_hash.get("cell", None), f_hash.get("devstage", None),
                              f_hash["antibody"], f_hash.get("lab", None),
                              f_hash.get("replicate", None), )
                        file_info[file_name] = f_hash
                
                fin.close()
                return(file_info)

	def parseTrack(self, trackPath, track_id, fileInfoHash):#
		"""
		Return object of class Track
		"""
		ind = track_id.rfind(".")
		track_id_name = track_id[0:ind]
		info = fileInfoHash[track_id_name]
		
		return Track(trackPath, info["antibody"], info.get("replicate", None), info.get("lab", "Unknown"), info.get("cell", None), info.get("devstage", None))
	
	def parseStatistic(self, fname, trackPathHash, resultPathHash, fileInfoHash, confounderHash):
		"""
		Parse statistic file
		param_id, resultPath are needed to form Run objects
		Return:
			tracks - dict of Track objects
			runList - list of Run objects
			trackPaths - set of paths for tracks
			labs - set of laboratory names
			tissues - set of tissues
			marks - set of marcs
			samples - set of samples
		"""
		runList = []
		fin = open(fname)
		tracks = {}
		trackPaths = set()
		labs = set()
		tissues = set()
		devstages = set()
		marks = set()
		samples = set()
		confounders = set()
	
		for line in fin:
			if line.startswith("id"):
				ids = line.split()
				continue
			ss = line.split("\t")
			data = {}
			for i in range(len(ids)):
				data[ids[i]]=ss[i]
			
			prog_run_id = data["id"]
			resultPath = resultPathHash[prog_run_id]
			trackPath = trackPathHash[prog_run_id]
			trackPaths.add(trackPath)
			
			#read track1, put to the list
			track1_name = data["name1"]
			track1_id = (trackPath, data["name1"])
			if track1_id not in tracks:
				track1 = self.parseTrack(trackPath, track1_name, fileInfoHash)
				labs.add(track1.lab)
				if (track1.tissue != None):
					tissues.add(track1.tissue)
				if (track1.devstage != None):
					devstages.add(track1.devstage)
				marks.add(track1.mark)
				if (track1.sample != None):
					samples.add(track1.sample)
				tracks[track1_id] = track1
			
			#read track2, put to the list
			track2_name = data["name2"]
			track2_id = (trackPath, track2_name)
			
			if track2_id not in tracks:
				track2 = self.parseTrack(trackPath, track2_name, fileInfoHash)
				labs.add(track2.lab)
				if (track2.tissue != None):
					tissues.add(track2.tissue)
				if (track2.devstage != None):
					devstages.add(track2.devstage)

				marks.add(track2.mark)
				if (track2.sample != None):
					samples.add(track2.sample)
				tracks[track2_id] = track2
			confounder = confounderHash.get(prog_run_id, None)
			if not confounder is None:
				confounderMemberPath = trackPathHash[prog_run_id].replace(confounder+".proj/", "")
				confounders.add((confounder, confounderMemberPath))
			#read other params
			
			runList.append(Run(resultPath, track1_id, track2_id, prog_run_id, data["nFgr"], data["nBkg"], data["Fg_Corr"], data["Fg_av_Corr"], data["FgCorr_sd"], data["Bg_Corr"], data["Bg_av_Corr"], data["BgCorr_sd"], data["Mann-Z"], data["p-value"],
	data["Date"], confounder))
		fin.close()

		return	tracks, runList, trackPaths, labs, tissues, devstages, marks, samples, confounders 
	
	def parseChrom(self, fname):
		"""
		Parse file with chromosome sizes
		Return hash of chromosome sizes
		"""
		fin = open(fname)
		chrom_hash = {}

		for line in fin:
			if line.startswith("#"):
				continue
			ss = line.split()
			chrom = ss[0]	
			size = ss[1]

			chrom_hash[chrom] = size	

		fin.close()
		return(chrom_hash)
	
	def parse_dist(self, fname):
		"""
		Parse distance correlation file
		Return:
		poses - position list, 
		chrom_dist_hash - distances by chromosome hash, 
		bg_dist - background distance value list
		"""
		print(fname)
		fin = open(fname)
		i = 0
		chrom_dist_hash = {}
		bg_dist = []
		poses = []
		
		names = []
		for line in fin:
			if line.startswith("#"):
				continue
			ss = line.split()
			if (i==0):
				names.append("All")
				names.extend(ss[5:])
				for name in names:
					chrom_dist_hash[name] = []		
			else:
				pose = int(ss[0])
				bg_dist.append(ss[1])
				chrom_dist_hash["All"].append([pose, float(ss[2])])

				for i in range(5,len(names)):
					if ss[i]!="NA":
						chrom_dist_hash[names[i]].append([pose, float(ss[i])])
					

			i+=1
	
		fin.close()

		return chrom_dist_hash, bg_dist

	def parseBg(self, fname):
		"""
		Parse background file
		Return list of background values
		"""
		fin = open(fname)
		bg = []
		for line in fin:
			bg.append(line.strip())


		fin.close()
		return(bg)

	def parseChromStat(self, fname):
		"""
		Parse statistic for chromosoms file
		Return dict of chromosom statistic
		"""
		fin = open(fname)
		chrom_stat = {}
		i=0
		for line in fin:
			if i < 3:
				i += 1
				continue
			chrom, av1, av2, cc, count = line.split()
			chrom_stat[chrom] = {'av1':av1, 'av2':av2, 'cc':cc, 'count':count}
		
		fin.close()
		return(chrom_stat)

	def parseFg(self, fname):
		"""
		Parse foreground file
		Return list of (chrom, score list) dicts
		"""
		fin = open(fname)
		fg = {}	

		for line in fin:
			chrom, start, end, score = line.split()
			#fg.append({'chrom':chrom, 'start':start, 'end':end, 'score':score})
			scores = fg.get(chrom, [])
			scores.append(score)
			fg[chrom] = scores

		fin.close()
		return(fg)
	def makePath(self, path, rel_path):
			abs_path = path
			dir = rel_path
			while dir.startswith("../"):
				l_ind = dir.lfind("/")
				r_ind = abs_path.rfind("/")
				dir = dir[l_ind+1:]
				abs_path = abs_path[0:r_ind]
			if dir.startswith("./"):
				dir = dir[2:]
			if dir.endswith("/"):
				dir = dir[0:(len(dir)-1)]
			return(abs_path + "/" + dir)

	def getConfounderName(self, path):
		"""
		Parse path, get confounder name if exists
		Return confounder name if exists, None otherwise
		"""
		elems = path.strip("/").split("/")
		name = elems[-1]
		if name.endswith(".proj"):
			return(name.replace(".proj", ""))
		return(None)
	def parseParam(self, fname):
		"""
		Parse parameters file
		Return dict of parameters
		"""
		#get path from paramFile
		ind = fname.rfind("/")
		path = fname[0:ind]
		
		fin = open(fname)
		paramParamHash = {}
		paramHash = {}
		trackPaths = {}
		resPaths = {}
		confounderNames = {}
		runId = ""
		for line in fin:
			line = line.strip()
			if line.startswith("id"):
				keys = line.split()
				continue
				
			values = line.split()
			for i in range(len(keys)):
				if keys[i] == "id":
					runId = values[i]
					continue
				if keys[i] == "trackPath":
					confounderName = self.getConfounderName(values[i])
					if not confounderName is None:
						confounderNames[runId] = confounderName
					trackPaths[runId] = self.makePath(path, values[i])
					continue
					
				if keys[i] == "resPath":
					resPaths[runId] = self.makePath(path, values[i])
					continue
				if keys[i] == "profPath":
					continue

					
				if keys[i] == "Rscript":
					continue
				if keys[i] == "Rscrpit":
					continue
				if keys[i] == "outSpectr":
					continue
				if keys[i] == "AutoCorr":
					continue

					
				key = keys[i]
				value = values[i]
				if key=="kernelType":
					if values[i]=="NORMAL":
						value = 1L
					elif values[i]=="LEFT_EXP":
						value = 2L
					else:
						value = 3L
					key = "kernelType_id"
				if key == "complFg":
					if values[i] == "IGNORE_STRAND":
						value = 1L
					elif values[i] == "COLINEAR":
						value = 2L
					else:
						value = 3L
					key = "complFg_id"
				if key == "NA":
					key = "na"
				if key == "bpType":
					if values[i] == "SCORE":
						value = 1L
					elif values[i] == "SIGNAL":
						value = 2L
					else:
						value = 3L
					key = "bpType_id"		
				if key == "intervals":
					if values[i] == "NONE":
						value = 1L
					elif values[i] == "GENE":
						value = 2L
					elif values[i] == "EXON":
						value = 3L
					elif values[i] == "IVS":
						value = 4L
					elif values[i] == "GENE_BEG":
						value = 5L
					elif values[i] == "EXON_BEG":
						value = 6L
					elif values[i] == "IVS_BEG":
						value = 7L
					elif values[i] == "GENE_END":
						value = 8L
					elif values[i] == "EXON_END":
						value = 9L
					elif values[i] == "IVS_END":
						value = 10L
					key = "intervals_id"
				if key == "LCScale":
					if values[i] == "LOG":
						value = 1L
					elif values[i] == "LIN":
						value = 2L
					else:
						value = 3L
					key = "lcscale_id"
				if key == "outLC":
					if values[i] == "NONE":
						value = 1L
					elif values[i] == "BASE":
						value = 2L
					elif values[i] == "CENTER":
						value = 3L
					elif values[i] == "BASE_MULT":
						value = 4L
					else:
						value = 5L
					key = "outLC_id"
				if key == "noiseLevel":
					value = str(int(float(values[i].strip())*100))
				if key == "LC_FDR":
					key = "lcFDR"
					value = str(int(float(values[i].strip())*100))
				paramHash[key] = value
			paramParamHash[runId] = Param(paramHash)
			paramHash = {}
		fin.close()
		
		return paramParamHash, trackPaths, resPaths, confounderNames
	def parseConfounder(self, fname, confounderMemberPath):
		"""
		Parse .cvr confounder file
		Return dict of members with eigen values and dict of paths
		"""
		fin = open(fname)
		confHash = {}
		paths = set()
		names = None
		eigen_values = None
		eigen = False
		for line in fin:
			line = line.strip()
			if names is None:
				names = line.split()
				continue
			if line.startswith("eigenValues"):
				eigen = True
				continue
			if eigen:
				eigen_values = line.split(";")
				for i in range(len(names)):
					path = confounderMemberPath + "/" + names[i]
					eigenValue = float(eigen_values[i].strip())
					confHash[names[i]] = ConfounderMember(names[i], path, eigenValue)
					paths.add(path)
				break
			
		fin.close()
		return(confHash, paths)
	def parseConfigParam(self, fname):
		"""
		Parse parameters Config file
		Return dict of parameters
		"""
		fin = open(fname)
		paramHash = {}
		for line in fin:
			line = line.strip()
			if line.startswith("#"):
				continue
			ss = re.split("[ =\t;]+", line)
			print(ss)
			if ss[0].strip()=="profPath":
				continue
			if ss[0].strip()=="trackPath":
				continue
			if ss[0].strip()=="resPath":
				continue
			if ss[0].strip()=="map":
				paramHash["map"] = ss[1].strip()
				continue
			if ss[0].strip()=="pcorProfile":
				paramHash["pcor_profile"] = ss[1].strip()
				continue
			if ss[0].strip()=="wSize":
				paramHash["wSize"] = ss[1].strip()
				continue
			if ss[0].strip()=="wStep":
				paramHash["wSize"] = ss[1].strip()
				continue

		
			if ss[0].strip()=="kernelType":
				id1 = 0L
				if ss[1].strip()=="NORMAL":
					id1 = 1L
				elif ss[1].strip()=="LEFT_EXP":
					id1 = 2L
				else:
					id1 = 3L
				paramHash["kernel_type_id"] = id1


				continue

			if ss[0].strip()=="KernelSigma":
				paramHash["kernel_sigma"] = ss[1].strip()
				continue

			if ss[0].strip()=="kernelShift":
				paramHash["kernel_shift"] = ss[1].strip()
				continue
		
			if ss[0].strip()=="kernelNS":
				paramHash["kernel_NS"] = ss[1].strip()
				continue

			if ss[0].strip()=="complFg":
				ss[1] = ss[1].strip()
				id1 = 0
				if ss[1] == "COLINEAR":
					id1 = 1
				elif ss[1] == "COMPLEMENT":
					id1 = 2
				else:
					id1 = 3

				paramHash["compl_Fg_id"] = id1
				continue

			if ss[0].strip()=="statistics":
#				paramHash["statistics"] = ss[1].strip()
				continue

			if ss[0].strip()=="aliases":
#				paramHash["aliases"] = ss[1].strip()
				continue

			if ss[0].strip()=="log":
#				paramHash["log"] = ss[1].strip()
				continue

			if ss[0].strip()=="chrom":
#				paramHash["chrom"] = ss[1].strip()
				continue

			if ss[0].strip()=="NA":
				paramHash["na"] = ss[1].strip()
				continue

			if ss[0].strip()=="type":                
				continue

			if ss[0].strip()=="intervals":


				intervals = ss[1].strip()
				id1 = 0

				if intervals == "NONE":
					id1 = 1
				elif intervals == "GENE":
					id1 = 2
				elif intervals == "EXON":
					id1 = 3
				elif intervals == "IVS":
					id1 = 4
				elif intervals == "GENE_BEG":
					id1 = 5
				elif intervals == "EXON_BEG":
					id1 = 6
				elif intervals == "IVS_BEG":
					id1 = 7
				elif intervals == "GENE_END":
					id1 = 8
				elif intervals == "EXON_END":
					id1 = 9
				elif intervals == "IVS_END":
					id1 = 10
				paramHash["gene_intervals_id"] = id1
				continue


			if ss[0].strip()=="strand":
				paramHash["strand"] = ss[1].strip()
				continue
		
			if ss[0].strip()=="scaleFactor":
				paramHash["scale_factor"] = ss[1].strip()
				continue

			if ss[0].strip()=="bin":
				paramHash["bin"] = ss[1].strip()
				continue

			if ss[0].strip()=="scale":
				scale = ss[1].strip()
				id1 = 0
				if intervals == "LOG":
					id1 = 1
				elif intervals == "LIN":
					id1 = 2
				elif intervals == "AUTO":
					id1 = 3

				paramHash["scale_id"] = id1
				continue

			if ss[0].strip()=="lAauto":
				paramHash["lAauto"] = ss[1].strip()
				continue


			if ss[0].strip()=="bpType":
				bpType = ss[1].strip()
				id1 = 0
				if bpType == "SCORE":
					id1 = 1
				elif bpType == "SIGNAL":
					id1 = 2
				elif bpType == "LOGPVAL":
					id1 = 3


				paramHash["bpType_id"] = id1
				continue
		
			if ss[0].strip()=="flankSize":
				paramHash["flankSize"] = ss[1].strip()
				continue

			if ss[0].strip()=="noiseLevel":
				paramHash["noiseLevel"] = str(int(float(ss[1].strip())*100))
				continue
		
			if ss[0].strip()=="maxNA":
				paramHash["maxNA"] = ss[1].strip()
				continue

			if ss[0].strip()=="maxZero":
				paramHash["maxZero"] = ss[1].strip()
				continue
			if ss[0].strip()=="nShuffle":
				paramHash["nShuffle"] = ss[1].strip()
				continue
			if ss[0].strip()=="maxShuffle":
				paramHash["maxShuffle"] = ss[1].strip()
				continue
			if ss[0].strip()=="minShuffle":
				paramHash["minShuffle"] = ss[1].strip()
				continue
             
		
			if ss[0].strip()=="threshold":
				paramHash["threshold"] = ss[1].strip()
				continue
			if ss[0].strip()=="corrOnly":
				paramHash["corrOnly"] = ss[1].strip()
				continue

			if ss[0].strip()=="mapIv":
				dist = ss[1].strip()
				id1 =  0
				if dist == "NONE":
					id1 = 1
				elif dist == "TOTAL":
					id1 = 2
				elif dist == "DETAIL":
					id1 = 3


				paramHash["distances_output_id"] = id1
				continue

			if ss[0].strip()=="outThreshold":
				paramHash["outThreshold"] = ss[1].strip()
				continue

			if ss[0].strip()=="outSpectr":
				paramHash["outSpectr"] = ss[1].strip()
				continue
			if ss[0].strip()=="outChrom":
				paramHash["outChrom"] = ss[1].strip()
				continue
			else:
				print("some param is not found: " + ss[0])

		fin.close()

		return Param(paramHash)

	


